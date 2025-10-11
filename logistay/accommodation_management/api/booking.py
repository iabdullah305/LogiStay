import frappe
from frappe.utils import getdate, validate_email_address
import re


@frappe.whitelist(allow_guest=True)
def lookup_employee_booking(employee_id=None, employee_name=None, phone=None):
    """Lookup employee accommodation booking (public access)"""
    try:
        # Validate at least one search parameter
        if not any([employee_id, employee_name, phone]):
            frappe.throw("Please provide employee ID, name, or phone number")
        
        # Build employee filters
        employee_filters = {}
        
        if employee_id:
            if not re.match(r'^[a-zA-Z0-9\-_]{1,20}$', employee_id):
                frappe.throw("Invalid employee ID format")
            employee_filters["name"] = employee_id
        
        if employee_name:
            if not re.match(r'^[a-zA-Z\s]{1,100}$', employee_name):
                frappe.throw("Invalid employee name format")
            employee_filters["employee_name"] = ["like", f"%{employee_name}%"]
        
        if phone:
            if not re.match(r'^[\+]?[0-9\-\s]{8,20}$', phone):
                frappe.throw("Invalid phone number format")
            employee_filters["phone"] = phone
        
        # Find employee
        employees = frappe.get_all(
            "Employee",
            fields=["name", "employee_name", "phone", "department"],
            filters=employee_filters,
            limit=5
        )
        
        if not employees:
            return {
                "employee_info": None,
                "accommodations": [],
                "message": "No employee found with the provided information"
            }
        
        # If multiple employees found, return list for selection
        if len(employees) > 1:
            return {
                "employee_info": None,
                "employees": employees,
                "accommodations": [],
                "message": "Multiple employees found. Please select one."
            }
        
        employee = employees[0]
        
        # Get accommodation assignments for this employee
        assignments = frappe.get_all(
            "Employee Accommodation Assignment",
            fields=[
                "name",
                "accommodation",
                "room", 
                "check_in_date",
                "check_out_date",
                "assignment_status",
                "authorized_supervisor"
            ],
            filters={"employee": employee["name"]},
            order_by="check_in_date desc",
            limit=10
        )
        
        # Enrich assignment data
        enriched_assignments = []
        for assignment in assignments:
            # Get accommodation details
            acc_info = frappe.get_value(
                "Accommodation",
                assignment["accommodation"],
                ["accommodation_name", "location"],
                as_dict=True
            )
            
            # Get room details
            room_info = frappe.get_value(
                "Room", 
                assignment["room"],
                ["room_number", "room_capacity"],
                as_dict=True
            )
            
            enriched_assignments.append({
                "assignment_id": assignment["name"],
                "accommodation_name": acc_info.get("accommodation_name") if acc_info else "Unknown",
                "location": acc_info.get("location") if acc_info else "Unknown",
                "room_number": room_info.get("room_number") if room_info else "Unknown",
                "room_capacity": room_info.get("room_capacity") if room_info else 1,
                "check_in_date": assignment["check_in_date"],
                "check_out_date": assignment["check_out_date"],
                "status": assignment["assignment_status"],
                "supervisor": assignment["authorized_supervisor"]
            })
        
        return {
            "employee_info": employee,
            "accommodations": enriched_assignments,
            "total_assignments": len(enriched_assignments)
        }
        
    except Exception as e:
        frappe.log_error(f"Error in employee booking lookup: {str(e)}")
        frappe.throw("Failed to lookup employee booking information")


@frappe.whitelist(allow_guest=True)
def get_room_details(room_id):
    """Get detailed room information (public access)"""
    try:
        # Validate room ID
        if not room_id or not re.match(r'^[a-zA-Z0-9\-_]{1,50}$', room_id):
            frappe.throw("Invalid room ID")
        
        # Get room details
        room = frappe.get_value(
            "Room",
            room_id,
            [
                "name", 
                "room_number", 
                "accommodation",
                "room_capacity", 
                "status"
            ],
            as_dict=True
        )
        
        if not room:
            frappe.throw("Room not found")
        
        # Get accommodation details
        accommodation = frappe.get_value(
            "Accommodation",
            room["accommodation"],
            [
                "accommodation_name",
                "location", 
                "status"
            ],
            as_dict=True
        )
        
        # Get current occupancy
        current_occupancy = frappe.db.count(
            "Employee Accommodation Assignment",
            {
                "room": room_id,
                "assignment_status": "Active"
            }
        )
        
        return {
            "room": {
                "id": room["name"],
                "room_number": room["room_number"],
                "capacity": room["room_capacity"],
                "status": room["status"],
                "current_occupancy": current_occupancy,
                "available_spaces": room["room_capacity"] - current_occupancy
            },
            "accommodation": {
                "name": accommodation.get("accommodation_name") if accommodation else "Unknown",
                "location": accommodation.get("location") if accommodation else "Unknown",
                "status": accommodation.get("status") if accommodation else "Unknown"
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting room details: {str(e)}")
        frappe.throw("Failed to load room details")