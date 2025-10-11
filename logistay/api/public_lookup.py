"""
Public Lookup API for Employee Trips and Shifts
Provides read-only access to sanitized fleet management data for public consumption.
"""

import frappe
from frappe import _
from frappe.utils import getdate, add_days, cint, flt
from frappe.rate_limiter import rate_limit
import re
from datetime import datetime, timedelta


# Whitelisted fields for public display - no PII
EMPLOYEE_FIELDS = [
    "name", "employee_code", "status", "hire_date"
]

TRIP_FIELDS = [
    "name", "trip_date", "status", "start_time", "end_time", 
    "source_location", "destination_location", "distance"
]

SHIFT_FIELDS = [
    "name", "shift_date", "shift_type", "status", "start_time", "end_time"
]

# Rate limiting configuration
RATE_LIMIT_PER_HOUR = 100
RATE_LIMIT_PER_MINUTE = 10

# Validation patterns
EMPLOYEE_CODE_PATTERN = r'^[A-Z0-9]{3,10}$'
DATE_PATTERN = r'^\d{4}-\d{2}-\d{2}$'
ID_PATTERN = r'^[A-Z0-9\-]{5,20}$'

# Maximum date range (days)
MAX_DATE_RANGE = 90


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=RATE_LIMIT_PER_HOUR, seconds=3600, methods=["POST", "GET"])
@rate_limit(limit=RATE_LIMIT_PER_MINUTE, seconds=60, methods=["POST", "GET"])
def lookup_employee_data(search_mode, search_value, date_from=None, date_to=None, limit=20, offset=0):
    """
    Public lookup for employee trips and shifts data.
    
    Args:
        search_mode: 'employee', 'shift', or 'trip'
        search_value: Employee code, shift ID, or trip ID
        date_from: Start date (YYYY-MM-DD format)
        date_to: End date (YYYY-MM-DD format)
        limit: Maximum records to return (1-50)
        offset: Pagination offset
    
    Returns:
        dict: Sanitized data with pagination info
    """
    try:
        # Log usage for monitoring (no sensitive data)
        _log_api_usage(search_mode, frappe.local.request_ip)
        
        # Validate and sanitize inputs
        validated_params = _validate_inputs(search_mode, search_value, date_from, date_to, limit, offset)
        
        # Execute search based on mode
        if validated_params['search_mode'] == 'employee':
            return _lookup_employee_records(validated_params)
        elif validated_params['search_mode'] == 'shift':
            return _lookup_shift_records(validated_params)
        elif validated_params['search_mode'] == 'trip':
            return _lookup_trip_records(validated_params)
        else:
            frappe.throw(_("Invalid search mode"), frappe.ValidationError)
            
    except frappe.ValidationError:
        raise
    except Exception as e:
        frappe.log_error(f"Public Lookup API Error: {str(e)}", "Public Lookup")
        frappe.throw(_("Service temporarily unavailable"), frappe.ServiceUnavailableError)


def _validate_inputs(search_mode, search_value, date_from, date_to, limit, offset):
    """Validate and sanitize all input parameters"""
    
    # Validate search mode
    valid_modes = ['employee', 'shift', 'trip']
    if search_mode not in valid_modes:
        frappe.throw(_("Invalid search mode. Must be: employee, shift, or trip"), frappe.ValidationError)
    
    # Validate search value based on mode
    if search_mode == 'employee':
        if not re.match(EMPLOYEE_CODE_PATTERN, search_value):
            frappe.throw(_("Invalid employee code format"), frappe.ValidationError)
    else:  # shift or trip
        if not re.match(ID_PATTERN, search_value):
            frappe.throw(_("Invalid ID format"), frappe.ValidationError)
    
    # Validate dates
    validated_date_from = None
    validated_date_to = None
    
    if date_from:
        if not re.match(DATE_PATTERN, date_from):
            frappe.throw(_("Invalid date format. Use YYYY-MM-DD"), frappe.ValidationError)
        try:
            validated_date_from = getdate(date_from)
        except:
            frappe.throw(_("Invalid date value"), frappe.ValidationError)
    
    if date_to:
        if not re.match(DATE_PATTERN, date_to):
            frappe.throw(_("Invalid date format. Use YYYY-MM-DD"), frappe.ValidationError)
        try:
            validated_date_to = getdate(date_to)
        except:
            frappe.throw(_("Invalid date value"), frappe.ValidationError)
    
    # Validate date range
    if validated_date_from and validated_date_to:
        if validated_date_from > validated_date_to:
            frappe.throw(_("Start date cannot be after end date"), frappe.ValidationError)
        
        date_diff = (validated_date_to - validated_date_from).days
        if date_diff > MAX_DATE_RANGE:
            frappe.throw(_("Date range cannot exceed 90 days"), frappe.ValidationError)
    
    # Validate pagination parameters
    limit = cint(limit)
    offset = cint(offset)
    
    if limit < 1 or limit > 50:
        frappe.throw(_("Limit must be between 1 and 50"), frappe.ValidationError)
    
    if offset < 0:
        frappe.throw(_("Offset cannot be negative"), frappe.ValidationError)
    
    return {
        'search_mode': search_mode,
        'search_value': search_value,
        'date_from': validated_date_from,
        'date_to': validated_date_to,
        'limit': limit,
        'offset': offset
    }


def _lookup_employee_records(params):
    """Lookup records for a specific employee"""
    
    # Check if employee exists and get basic info
    employee_filters = {
        'employee_code': params['search_value'],
        'status': 'Active'
    }
    
    employee = frappe.db.get_value('Fleet Driver', employee_filters, EMPLOYEE_FIELDS, as_dict=True)
    if not employee:
        return {
            'success': True,
            'data': {
                'employee': None,
                'trips': [],
                'shifts': [],
                'total_records': 0
            },
            'message': 'No active employee found with this code'
        }
    
    # Build date filters
    date_filters = {}
    if params['date_from']:
        date_filters['>='] = params['date_from']
    if params['date_to']:
        date_filters['<='] = params['date_to']
    
    # Get trips for this employee
    trip_filters = {'driver': employee['name']}
    if date_filters:
        trip_filters['trip_date'] = date_filters
    
    trips = frappe.db.get_list(
        'Fleet Trip',
        filters=trip_filters,
        fields=TRIP_FIELDS,
        order_by='trip_date desc, creation desc',
        limit=params['limit'],
        start=params['offset']
    )
    
    # Get shifts for this employee
    shift_filters = {'driver': employee['name']}
    if date_filters:
        shift_filters['shift_date'] = date_filters
    
    shifts = frappe.db.get_list(
        'Fleet Shift',
        filters=shift_filters,
        fields=SHIFT_FIELDS,
        order_by='shift_date desc, creation desc',
        limit=params['limit'],
        start=params['offset']
    )
    
    # Get total count for pagination
    total_trips = frappe.db.count('Fleet Trip', trip_filters)
    total_shifts = frappe.db.count('Fleet Shift', shift_filters)
    
    return {
        'success': True,
        'data': {
            'employee': employee,
            'trips': trips,
            'shifts': shifts,
            'total_records': total_trips + total_shifts,
            'pagination': {
                'limit': params['limit'],
                'offset': params['offset'],
                'total_trips': total_trips,
                'total_shifts': total_shifts
            }
        }
    }


def _lookup_shift_records(params):
    """Lookup specific shift record"""
    
    shift = frappe.db.get_value(
        'Fleet Shift',
        params['search_value'],
        SHIFT_FIELDS + ['driver'],
        as_dict=True
    )
    
    if not shift:
        return {
            'success': True,
            'data': {
                'shift': None,
                'employee': None
            },
            'message': 'Shift not found'
        }
    
    # Get employee info if shift exists
    employee = None
    if shift.get('driver'):
        employee = frappe.db.get_value(
            'Fleet Driver',
            shift['driver'],
            EMPLOYEE_FIELDS,
            as_dict=True
        )
    
    # Remove driver field from shift data (not in whitelist)
    shift.pop('driver', None)
    
    return {
        'success': True,
        'data': {
            'shift': shift,
            'employee': employee
        }
    }


def _lookup_trip_records(params):
    """Lookup specific trip record"""
    
    trip = frappe.db.get_value(
        'Fleet Trip',
        params['search_value'],
        TRIP_FIELDS + ['driver'],
        as_dict=True
    )
    
    if not trip:
        return {
            'success': True,
            'data': {
                'trip': None,
                'employee': None
            },
            'message': 'Trip not found'
        }
    
    # Get employee info if trip exists
    employee = None
    if trip.get('driver'):
        employee = frappe.db.get_value(
            'Fleet Driver',
            trip['driver'],
            EMPLOYEE_FIELDS,
            as_dict=True
        )
    
    # Remove driver field from trip data (not in whitelist)
    trip.pop('driver', None)
    
    return {
        'success': True,
        'data': {
            'trip': trip,
            'employee': employee
        }
    }


def _log_api_usage(search_mode, ip_address):
    """Log API usage for monitoring (non-intrusive, no sensitive data)"""
    try:
        # Only log if Fleet Access Log doctype exists
        if frappe.db.exists('DocType', 'Fleet Access Log'):
            frappe.get_doc({
                'doctype': 'Fleet Access Log',
                'user': 'Guest',
                'document_type': 'Public Lookup API',
                'document_name': search_mode,
                'action': 'lookup',
                'success': True,
                'timestamp': frappe.utils.now(),
                'ip_address': ip_address,
                'additional_info': f'Search mode: {search_mode}'
            }).insert(ignore_permissions=True)
    except Exception:
        # Silently fail - logging should not break the API
        pass


@frappe.whitelist(allow_guest=True)
def get_api_info():
    """Get API information and usage limits"""
    return {
        'success': True,
        'data': {
            'api_version': '1.0',
            'rate_limits': {
                'per_hour': RATE_LIMIT_PER_HOUR,
                'per_minute': RATE_LIMIT_PER_MINUTE
            },
            'search_modes': ['employee', 'shift', 'trip'],
            'max_date_range_days': MAX_DATE_RANGE,
            'max_records_per_request': 50,
            'supported_date_format': 'YYYY-MM-DD'
        }
    }