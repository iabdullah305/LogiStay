"""
Driver API endpoints for Fleet Management Self-Service
All endpoints are whitelisted and include proper permission checks
"""

import frappe
from frappe import _
import frappe.utils
from frappe.utils import now, getdate, flt, cint
from frappe.model.document import Document
import json


@frappe.whitelist()
def get_driver_dashboard():
    """
    Get driver dashboard data including KPIs and recent activity
    Returns: dict with dashboard metrics
    """
    try:
        # Get current user's employee record
        employee = get_current_employee()
        if not employee:
            frappe.throw(_("No employee record found for current user"))
        
        # Get driver record
        driver = frappe.get_value("Fleet Driver", {"employee": employee.name}, ["name", "status"])
        if not driver:
            frappe.throw(_("No driver record found for current employee"))
        
        # Get active assignments
        active_assignments = frappe.db.count("Driver Vehicle Assignment", {
            "driver": driver[0],
            "status": "Active",
            "docstatus": 1
        })
        
        # Get today's trips
        today_trips = frappe.db.count("Fleet Trip", {
            "driver": driver[0],
            "trip_date": getdate(),
            "docstatus": ["!=", 2]
        })
        
        # Get pending tasks (trips with status 'Assigned' or 'In Progress')
        pending_tasks = frappe.db.count("Fleet Trip", {
            "driver": driver[0],
            "status": ["in", ["Assigned", "In Progress"]],
            "docstatus": ["!=", 2]
        })
        
        # Get this month's fuel entries
        from frappe.utils.data import get_first_day_of_month
        month_fuel_entries = frappe.db.count("Fuel Entry", {
            "driver": driver[0],
            "fuel_date": [">=", get_first_day_of_month(getdate())],
            "docstatus": 1
        })
        
        # Get recent activity (last 5 trips)
        recent_trips = frappe.db.get_list("Fleet Trip", {
            "driver": driver[0],
            "docstatus": ["!=", 2]
        }, ["name", "vehicle", "status", "trip_date", "start_time", "end_time"], 
        order_by="creation desc", limit=5)
        
        # Get vehicle status for current assignment
        current_vehicle = frappe.db.get_value("Driver Vehicle Assignment", {
            "driver": driver[0],
            "status": "Active",
            "docstatus": 1
        }, ["vehicle", "assignment_date"], order_by="creation desc")
        
        vehicle_status = None
        if current_vehicle:
            vehicle_info = frappe.get_doc("Fleet Vehicle", current_vehicle[0])
            vehicle_status = {
                "vehicle_number": vehicle_info.vehicle_number,
                "make": vehicle_info.make,
                "model": vehicle_info.model,
                "status": vehicle_info.status,
                "assignment_date": current_vehicle[1]
            }
        
        return {
            "kpis": {
                "active_assignments": active_assignments,
                "today_trips": today_trips,
                "pending_tasks": pending_tasks,
                "month_fuel_entries": month_fuel_entries
            },
            "recent_activity": recent_trips,
            "vehicle_status": vehicle_status,
            "driver_status": driver[1]
        }
        
    except Exception as e:
        frappe.log_error(f"Driver Dashboard Error: {str(e)}")
        frappe.throw(_("Failed to load dashboard data"))


@frappe.whitelist()
def get_trips(status=None, limit=20, offset=0):
    """
    Get driver trips with optional status filter
    Args:
        status: Trip status filter (optional)
        limit: Number of records to return
        offset: Pagination offset
    Returns: list of trip records
    """
    try:
        employee = get_current_employee()
        if not employee:
            frappe.throw(_("No employee record found"))
        
        driver = frappe.get_value("Fleet Driver", {"employee": employee.name}, "name")
        if not driver:
            frappe.throw(_("No driver record found"))
        
        # Build filters
        filters = {
            "driver": driver,
            "docstatus": ["!=", 2]
        }
        
        if status and status != "all":
            filters["status"] = status
        
        # Get trips
        trips = frappe.db.get_list("Fleet Trip", 
            filters=filters,
            fields=[
                "name", "vehicle", "status", "trip_date", "start_time", 
                "end_time", "start_location", "end_location", "distance",
                "creation", "modified"
            ],
            order_by="trip_date desc, creation desc",
            limit=limit,
            start=offset
        )
        
        # Enhance with vehicle information
        for trip in trips:
            if trip.vehicle:
                vehicle_info = frappe.get_value("Fleet Vehicle", trip.vehicle, 
                    ["vehicle_number", "make", "model"], as_dict=True)
                if vehicle_info:
                    trip.update(vehicle_info)
        
        return trips
        
    except Exception as e:
        frappe.log_error(f"Get Trips Error: {str(e)}")
        frappe.throw(_("Failed to load trips"))


@frappe.whitelist()
def update_trip_status(trip_id, action):
    """
    Update trip status based on driver action
    Args:
        trip_id: Fleet Trip document name
        action: Action to perform (accept, start, pause, complete)
    Returns: Updated trip status
    """
    try:
        # Validate permissions
        employee = get_current_employee()
        if not employee:
            frappe.throw(_("No employee record found"))
        
        driver = frappe.get_value("Fleet Driver", {"employee": employee.name}, "name")
        if not driver:
            frappe.throw(_("No driver record found"))
        
        # Get trip document
        trip = frappe.get_doc("Fleet Trip", trip_id)
        
        # Verify driver ownership
        if trip.driver != driver:
            frappe.throw(_("You are not authorized to modify this trip"))
        
        # Validate action based on current status
        valid_actions = {
            "Assigned": ["accept", "reject"],
            "Accepted": ["start"],
            "In Progress": ["pause", "complete"],
            "Paused": ["start", "complete"]
        }
        
        if action not in valid_actions.get(trip.status, []):
            frappe.throw(_("Invalid action for current trip status"))
        
        # Update status based on action
        status_mapping = {
            "accept": "Accepted",
            "reject": "Rejected", 
            "start": "In Progress",
            "pause": "Paused",
            "complete": "Completed"
        }
        
        trip.status = status_mapping[action]
        
        # Set timestamps
        if action == "start":
            trip.start_time = now()
        elif action == "complete":
            trip.end_time = now()
        
        # Save with permissions check
        trip.save(ignore_permissions=False)
        
        # Submit if completed
        if action == "complete" and trip.docstatus == 0:
            trip.submit()
        
        return {
            "status": trip.status,
            "start_time": trip.start_time,
            "end_time": trip.end_time
        }
        
    except Exception as e:
        frappe.log_error(f"Update Trip Status Error: {str(e)}")
        frappe.throw(_("Failed to update trip status"))


@frappe.whitelist()
def create_fuel_entry(vehicle, fuel_date, quantity, amount, vendor=None, receipt_attachment=None):
    """
    Create a new fuel entry
    Args:
        vehicle: Fleet Vehicle name
        fuel_date: Date of fuel purchase
        quantity: Fuel quantity in liters
        amount: Fuel cost
        vendor: Vendor/station name (optional)
        receipt_attachment: Receipt file URL (optional)
    Returns: Created fuel entry name
    """
    try:
        # Validate permissions
        employee = get_current_employee()
        if not employee:
            frappe.throw(_("No employee record found"))
        
        driver = frappe.get_value("Fleet Driver", {"employee": employee.name}, "name")
        if not driver:
            frappe.throw(_("No driver record found"))
        
        # Validate vehicle assignment
        is_assigned = frappe.db.exists("Driver Vehicle Assignment", {
            "driver": driver,
            "vehicle": vehicle,
            "status": "Active",
            "docstatus": 1
        })
        
        if not is_assigned:
            frappe.throw(_("You are not assigned to this vehicle"))
        
        # Validate inputs
        if not fuel_date or not quantity or not amount:
            frappe.throw(_("Fuel date, quantity, and amount are required"))
        
        if flt(quantity) <= 0:
            frappe.throw(_("Quantity must be greater than zero"))
        
        if flt(amount) <= 0:
            frappe.throw(_("Amount must be greater than zero"))
        
        if getdate(fuel_date) > getdate():
            frappe.throw(_("Fuel date cannot be in the future"))

        # Validate against Fleet Settings
        from logistay.fleet_management.doctype.fleet_settings.fleet_settings import (
            validate_fuel_entry_against_settings
        )
        validate_fuel_entry_against_settings(flt(quantity), flt(amount), fuel_date)

        # Create fuel entry
        fuel_entry = frappe.new_doc("Fuel Entry")
        fuel_entry.vehicle = vehicle
        fuel_entry.driver = driver
        fuel_entry.fuel_date = fuel_date
        fuel_entry.quantity = flt(quantity)
        fuel_entry.amount = flt(amount)
        fuel_entry.price_per_liter = flt(amount) / flt(quantity)
        
        if vendor:
            fuel_entry.vendor = vendor
        
        if receipt_attachment:
            fuel_entry.receipt_attachment = receipt_attachment
        
        # Save and submit
        fuel_entry.insert(ignore_permissions=False)
        fuel_entry.submit()
        
        return fuel_entry.name
        
    except Exception as e:
        frappe.log_error(f"Create Fuel Entry Error: {str(e)}")
        frappe.throw(_("Failed to create fuel entry"))


@frappe.whitelist()
def get_fuel_entries(limit=20, offset=0):
    """
    Get driver's fuel entries
    Args:
        limit: Number of records to return
        offset: Pagination offset
    Returns: list of fuel entry records
    """
    try:
        employee = get_current_employee()
        if not employee:
            frappe.throw(_("No employee record found"))
        
        driver = frappe.get_value("Fleet Driver", {"employee": employee.name}, "name")
        if not driver:
            frappe.throw(_("No driver record found"))
        
        # Get fuel entries
        entries = frappe.db.get_list("Fuel Entry",
            filters={"driver": driver},
            fields=[
                "name", "vehicle", "fuel_date", "quantity", "amount", 
                "price_per_liter", "vendor", "docstatus", "creation"
            ],
            order_by="fuel_date desc, creation desc",
            limit=limit,
            start=offset
        )
        
        # Enhance with vehicle information
        for entry in entries:
            if entry.vehicle:
                vehicle_info = frappe.get_value("Fleet Vehicle", entry.vehicle,
                    ["vehicle_number", "make", "model"], as_dict=True)
                if vehicle_info:
                    entry.update(vehicle_info)
        
        return entries
        
    except Exception as e:
        frappe.log_error(f"Get Fuel Entries Error: {str(e)}")
        frappe.throw(_("Failed to load fuel entries"))


@frappe.whitelist()
def get_assigned_vehicles():
    """
    Get vehicles assigned to current driver
    Returns: list of assigned vehicles
    """
    try:
        employee = get_current_employee()
        if not employee:
            frappe.throw(_("No employee record found"))
        
        driver = frappe.get_value("Fleet Driver", {"employee": employee.name}, "name")
        if not driver:
            frappe.throw(_("No driver record found"))
        
        # Get assigned vehicles
        assignments = frappe.db.get_list("Driver Vehicle Assignment",
            filters={
                "driver": driver,
                "status": "Active",
                "docstatus": 1
            },
            fields=["vehicle"],
            order_by="creation desc"
        )
        
        vehicles = []
        for assignment in assignments:
            vehicle_info = frappe.get_value("Fleet Vehicle", assignment.vehicle,
                ["name", "vehicle_number", "make", "model", "status"], as_dict=True)
            if vehicle_info:
                vehicles.append(vehicle_info)
        
        return vehicles
        
    except Exception as e:
        frappe.log_error(f"Get Assigned Vehicles Error: {str(e)}")
        frappe.throw(_("Failed to load assigned vehicles"))


@frappe.whitelist()
def get_profile():
    """
    Get driver profile information
    Returns: dict with profile data
    """
    try:
        employee = get_current_employee()
        if not employee:
            frappe.throw(_("No employee record found"))
        
        # Get driver information
        driver_info = frappe.get_value("Fleet Driver", {"employee": employee.name},
            ["name", "license_number", "license_expiry_date", "experience_years", "status"],
            as_dict=True)
        
        # Get current assignment
        current_assignment = frappe.db.get_value("Driver Vehicle Assignment", {
            "driver": driver_info.name if driver_info else None,
            "status": "Active",
            "docstatus": 1
        }, ["vehicle", "assignment_date"], order_by="creation desc", as_dict=True)
        
        assignment_details = None
        if current_assignment:
            vehicle_info = frappe.get_value("Fleet Vehicle", current_assignment.vehicle,
                ["vehicle_number", "make", "model", "status"], as_dict=True)
            if vehicle_info:
                assignment_details = {
                    **vehicle_info,
                    "assignment_date": current_assignment.assignment_date,
                    "status": "Active"
                }
        
        return {
            "employee": employee,
            "driver_info": driver_info,
            "current_assignment": assignment_details
        }
        
    except Exception as e:
        frappe.log_error(f"Get Profile Error: {str(e)}")
        frappe.throw(_("Failed to load profile"))


@frappe.whitelist()
def change_password(current_password, new_password):
    """
    Change user password
    Args:
        current_password: Current password
        new_password: New password
    Returns: Success message
    """
    try:
        user = frappe.session.user
        
        # Verify current password
        from frappe.utils.password import check_password
        if not check_password(user, current_password):
            return {"success": False, "error": _("Current password is incorrect")}
        
        # Validate new password
        if len(new_password) < 8:
            return {"success": False, "error": _("New password must be at least 8 characters long")}
        
        # Update password
        from frappe.utils.password import update_password
        update_password(user, new_password)
        
        return {"success": True, "message": _("Password updated successfully")}
        
    except Exception as e:
        frappe.log_error(f"Change Password Error: {str(e)}")
        return {"success": False, "error": _("Failed to change password")}


@frappe.whitelist()
def create_support_ticket(category, priority, subject, description, attachment=None):
    """
    Create a support ticket
    Args:
        category: Issue category
        priority: Ticket priority
        subject: Ticket subject
        description: Detailed description
        attachment: File attachment URL (optional)
    Returns: Created ticket name
    """
    try:
        employee = get_current_employee()
        if not employee:
            return {"success": False, "error": _("No employee record found")}
        
        # Validate inputs
        if not all([category, priority, subject, description]):
            return {"success": False, "error": _("Category, priority, subject, and description are required")}
        
        # Create Issue document (standard Frappe DocType for support tickets)
        issue = frappe.new_doc("Issue")
        issue.subject = subject
        issue.description = description
        issue.issue_type = category
        issue.priority = priority
        issue.raised_by = frappe.session.user
        
        # Add custom fields if they exist
        if hasattr(issue, 'employee'):
            issue.employee = employee.name
        
        if attachment:
            # Create file attachment
            file_doc = frappe.new_doc("File")
            file_doc.file_url = attachment
            file_doc.attached_to_doctype = "Issue"
            file_doc.is_private = 1
            file_doc.insert()
            
            # Link to issue after saving
            issue.insert(ignore_permissions=False)
            file_doc.attached_to_name = issue.name
            file_doc.save()
        else:
            issue.insert(ignore_permissions=False)
        
        return {"success": True, "ticket_id": issue.name}
        
    except Exception as e:
        frappe.log_error(f"Create Support Ticket Error: {str(e)}")
        return {"success": False, "error": _("Failed to create support ticket")}


@frappe.whitelist()
def get_support_tickets(limit=20, offset=0):
    """
    Get user's support tickets
    Args:
        limit: Number of records to return
        offset: Pagination offset
    Returns: list of support tickets
    """
    try:
        # Get tickets raised by current user
        tickets = frappe.db.get_list("Issue",
            filters={"raised_by": frappe.session.user},
            fields=[
                "name", "subject", "description", "issue_type as category",
                "priority", "status", "creation", "modified"
            ],
            order_by="creation desc",
            limit=limit,
            start=offset
        )
        
        return {"tickets": tickets}
        
    except Exception as e:
        frappe.log_error(f"Get Support Tickets Error: {str(e)}")
        return {"tickets": []}


@frappe.whitelist()
def get_driver_info():
    """
    Get detailed driver information
    Returns: driver record details
    """
    try:
        employee = get_current_employee()
        if not employee:
            frappe.throw(_("No employee record found"))
        
        driver_info = frappe.get_value("Fleet Driver", {"employee": employee.name},
            ["name", "license_number", "license_expiry_date", "experience_years", 
             "status", "phone", "emergency_contact"], as_dict=True)
        
        return driver_info
        
    except Exception as e:
        frappe.log_error(f"Get Driver Info Error: {str(e)}")
        frappe.throw(_("Failed to load driver information"))


@frappe.whitelist()
def get_current_assignment():
    """
    Get current vehicle assignment details
    Returns: current assignment information
    """
    try:
        employee = get_current_employee()
        if not employee:
            frappe.throw(_("No employee record found"))
        
        driver = frappe.get_value("Fleet Driver", {"employee": employee.name}, "name")
        if not driver:
            frappe.throw(_("No driver record found"))
        
        # Get current assignment
        assignment = frappe.db.get_value("Driver Vehicle Assignment", {
            "driver": driver,
            "status": "Active",
            "docstatus": 1
        }, ["vehicle", "assignment_date", "route"], order_by="creation desc", as_dict=True)
        
        if not assignment:
            return None
        
        # Get vehicle details
        vehicle_info = frappe.get_value("Fleet Vehicle", assignment.vehicle,
            ["vehicle_number", "make", "model", "status"], as_dict=True)
        
        if vehicle_info:
            assignment.update(vehicle_info)
        
        return assignment
        
    except Exception as e:
        frappe.log_error(f"Get Current Assignment Error: {str(e)}")
        frappe.throw(_("Failed to load current assignment"))


def get_current_employee():
    """
    Helper function to get current user's employee record
    Returns: Employee document or None
    """
    user = frappe.session.user
    employee_name = frappe.db.get_value("Employee", {"user_id": user}, "name")
    
    if employee_name:
        return frappe.get_doc("Employee", employee_name)
    
    return None


def validate_driver_permissions(driver_name):
    """
    Helper function to validate if current user can access driver data
    Args:
        driver_name: Fleet Driver document name
    Returns: Boolean
    """
    employee = get_current_employee()
    if not employee:
        return False
    
    driver_employee = frappe.get_value("Fleet Driver", driver_name, "employee")
    return driver_employee == employee.name