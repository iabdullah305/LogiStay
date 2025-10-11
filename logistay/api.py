import frappe
from frappe.utils import now, getdate, validate_email_address
import re


@frappe.whitelist()
def get_counts():
    """Return key DocType counts without writing to DB."""
    doctypes = [
        "Fleet Vehicle",
        "Fleet Driver",
        "Fuel Entry",
        "Driver Vehicle Assignment",
        "Supplier Master",
        "Supplier Contract",
    ]
    data = {"timestamp": now(), "counts": {}}
    for dt in doctypes:
        try:
            data["counts"][dt] = frappe.db.count(dt)
        except Exception:
            data["counts"][dt] = 0
    return data


@frappe.whitelist()
def fuel_entries_today(limit: int = 10):
    """Return today's Fuel Entry list (read-only)."""
    today = getdate()
    rows = frappe.get_all(
        "Fuel Entry",
        fields=["name", "posting_date", "vehicle", "liters", "amount"],
        filters={"posting_date": today},
        limit=limit,
        order_by="posting_date desc, name desc",
    )
    return {"timestamp": now(), "items": rows}


@frappe.whitelist()
def get_fleet_statistics():
    """Get fleet management statistics for dashboard."""
    try:
        stats = {
            "total_vehicles": frappe.db.count("Fleet Vehicle", {"status": ["!=", "Disposed"]}),
            "active_drivers": frappe.db.count("Fleet Driver", {"status": "Active"}),
            "ongoing_trips": frappe.db.count("Fleet Trip", {"status": "In Progress"}),
            "fuel_entries_today": frappe.db.count("Fuel Entry", {"posting_date": getdate()})
        }
        return stats
    except Exception as e:
        frappe.log_error(f"Error getting fleet statistics: {str(e)}")
        return {
            "total_vehicles": 0,
            "active_drivers": 0,
            "ongoing_trips": 0,
            "fuel_entries_today": 0
        }


@frappe.whitelist()
def get_todays_fuel_entries():
    """Get today's fuel entries with minimal fields."""
    try:
        today = getdate()
        entries = frappe.get_all(
            "Fuel Entry",
            fields=["name", "vehicle", "driver", "fuel_amount", "total_cost", "posting_date"],
            filters={"posting_date": today},
            order_by="creation desc",
            limit=20
        )
        return entries
    except Exception as e:
        frappe.log_error(f"Error getting fuel entries: {str(e)}")
        return []


@frappe.whitelist()
def get_current_driver_profile():
    """Get current driver's profile information."""
    try:
        user = frappe.session.user
        if user == "Guest":
            frappe.throw("Authentication required")
        
        # Find driver record linked to current user
        driver = frappe.get_all(
            "Fleet Driver",
            fields=["name", "full_name", "employee", "phone", "email", "status", "date_of_birth", "address"],
            filters={"user": user},
            limit=1
        )
        
        if driver:
            return driver[0]
        else:
            frappe.throw("Driver profile not found")
            
    except Exception as e:
        frappe.log_error(f"Error getting driver profile: {str(e)}")
        frappe.throw("Failed to load driver profile")


@frappe.whitelist()
def get_driver_trips(filters=None):
    """Get driver's trips with optional filters."""
    try:
        user = frappe.session.user
        if user == "Guest":
            frappe.throw("Authentication required")
        
        # Find driver record
        driver = frappe.get_value("Fleet Driver", {"user": user}, "name")
        if not driver:
            frappe.throw("Driver not found")
        
        # Build filters
        trip_filters = {"driver": driver}
        if filters:
            if filters.get("status"):
                trip_filters["status"] = filters["status"]
            if filters.get("dateFrom"):
                trip_filters["trip_date"] = [">=", filters["dateFrom"]]
            if filters.get("dateTo"):
                if "trip_date" in trip_filters:
                    trip_filters["trip_date"] = ["between", [filters["dateFrom"], filters["dateTo"]]]
                else:
                    trip_filters["trip_date"] = ["<=", filters["dateTo"]]
        
        trips = frappe.get_all(
            "Fleet Trip",
            fields=["name", "route", "vehicle", "trip_date", "start_time", "end_time", "status", "purpose"],
            filters=trip_filters,
            order_by="trip_date desc, creation desc",
            limit=50
        )
        
        return trips
        
    except Exception as e:
        frappe.log_error(f"Error getting driver trips: {str(e)}")
        return []


def _validate_employee_search_params(employee_id, employee_name):
    """Validate employee search parameters."""
    if not employee_id and not employee_name:
        frappe.throw("Either Employee ID or Employee Name is required")
    
    if employee_id:
        # Validate employee ID format (alphanumeric, max 20 chars)
        if not re.match(r'^[a-zA-Z0-9-_]{1,20}$', employee_id):
            frappe.throw("Invalid Employee ID format")
    
    if employee_name:
        # Validate name (letters, spaces, max 100 chars)
        if not re.match(r'^[a-zA-Z\s]{1,100}$', employee_name):
            frappe.throw("Invalid Employee Name format")


@frappe.whitelist()
def search_employee_trips_shifts(employee_id=None, employee_name=None, date_from=None, date_to=None):
    """Search for employee trips and shifts with strict validation."""
    try:
        # Validate input parameters
        _validate_employee_search_params(employee_id, employee_name)
        
        # Build employee filters
        employee_filters = {}
        if employee_id:
            employee_filters["name"] = employee_id
        if employee_name:
            employee_filters["employee_name"] = ["like", f"%{employee_name}%"]
        
        # Find employee
        employee_info = frappe.get_all(
            "Employee",
            fields=["name", "employee_name", "department", "designation", "status"],
            filters=employee_filters,
            limit=1
        )
        
        if not employee_info:
            return {
                "employee_info": None,
                "trips": [],
                "shifts": []
            }
        
        employee = employee_info[0]
        
        # Build date filters
        date_filters = {}
        if date_from:
            date_filters["trip_date"] = [">=", date_from]
        if date_to:
            if "trip_date" in date_filters:
                date_filters["trip_date"] = ["between", [date_from, date_to]]
            else:
                date_filters["trip_date"] = ["<=", date_to]
        
        # Get trips for employee
        trip_filters = {"employee": employee["name"]}
        trip_filters.update(date_filters)
        
        trips = frappe.get_all(
            "Fleet Trip",
            fields=["name", "route", "vehicle", "trip_date", "start_time", "end_time", "status", "purpose"],
            filters=trip_filters,
            order_by="trip_date desc",
            limit=100
        )
        
        # Get shifts for employee (if shift doctype exists)
        shifts = []
        try:
            shift_filters = {"employee": employee["name"]}
            if date_from or date_to:
                shift_date_filters = {}
                if date_from:
                    shift_date_filters["shift_date"] = [">=", date_from]
                if date_to:
                    if "shift_date" in shift_date_filters:
                        shift_date_filters["shift_date"] = ["between", [date_from, date_to]]
                    else:
                        shift_date_filters["shift_date"] = ["<=", date_to]
                shift_filters.update(shift_date_filters)
            
            shifts = frappe.get_all(
                "Employee Shift",
                fields=["name", "shift_type", "shift_date", "start_time", "end_time", "status", "department"],
                filters=shift_filters,
                order_by="shift_date desc",
                limit=100
            )
        except Exception:
            # Shift doctype might not exist
            shifts = []
        
        return {
            "employee_info": employee,
            "trips": trips,
            "shifts": shifts
        }
        
    except Exception as e:
        frappe.log_error(f"Error searching employee data: {str(e)}")
        frappe.throw("Failed to search employee data")