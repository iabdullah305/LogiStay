import frappe
from frappe.utils import validate_email_address, getdate
import re


@frappe.whitelist(allow_guest=True)
def get_accommodations(limit=20, search_term=None):
    """Get list of accommodations with basic info (public access)"""
    try:
        filters = {"status": ["!=", "Inactive"]}
        
        if search_term:
            # Validate search term
            if not re.match(r'^[a-zA-Z0-9\s\-_]{1,50}$', search_term):
                frappe.throw("Invalid search term format")
            
            filters["accommodation_name"] = ["like", f"%{search_term}%"]
        
        accommodations = frappe.get_all(
            "Accommodation",
            fields=[
                "name", 
                "accommodation_name", 
                "location", 
                "status",
                "accommodation_capacity",
                "accommodation_occupancy"
            ],
            filters=filters,
            order_by="accommodation_name asc",
            limit=int(limit) if limit else 20
        )
        
        return {
            "accommodations": accommodations,
            "total_count": len(accommodations)
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting accommodations: {str(e)}")
        return {"accommodations": [], "total_count": 0}


@frappe.whitelist(allow_guest=True)
def get_accommodation_details(accommodation_id):
    """Get detailed accommodation information (public access)"""
    try:
        # Validate accommodation ID
        if not accommodation_id or not re.match(r'^[a-zA-Z0-9\-_]{1,50}$', accommodation_id):
            frappe.throw("Invalid accommodation ID")
        
        # Get accommodation details
        accommodation = frappe.get_doc("Accommodation", accommodation_id)
        
        if accommodation.status == "Inactive":
            frappe.throw("Accommodation not available")
        
        # Get rooms for this accommodation
        rooms = frappe.get_all(
            "Room",
            fields=[
                "name",
                "room_number", 
                "room_capacity",
                "status"
            ],
            filters={
                "accommodation": accommodation_id,
                "status": ["!=", "Out of Service"]
            },
            order_by="room_number asc"
        )
        
        return {
            "accommodation": {
                "name": accommodation.name,
                "accommodation_name": accommodation.accommodation_name,
                "location": accommodation.location,
                "status": accommodation.status,
                "capacity": accommodation.accommodation_capacity,
                "occupancy": accommodation.accommodation_occupancy,
                "availability": accommodation.accommodation_capacity - accommodation.accommodation_occupancy
            },
            "rooms": rooms
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting accommodation details: {str(e)}")
        frappe.throw("Failed to load accommodation details")


@frappe.whitelist(allow_guest=True)
def check_availability(accommodation_id=None, check_in_date=None, check_out_date=None):
    """Check room availability for given dates (public access)"""
    try:
        # Validate inputs
        if accommodation_id and not re.match(r'^[a-zA-Z0-9\-_]{1,50}$', accommodation_id):
            frappe.throw("Invalid accommodation ID")
        
        if check_in_date:
            try:
                check_in_date = getdate(check_in_date)
            except:
                frappe.throw("Invalid check-in date format")
        
        if check_out_date:
            try:
                check_out_date = getdate(check_out_date)
            except:
                frappe.throw("Invalid check-out date format")
        
        if check_in_date and check_out_date and check_in_date >= check_out_date:
            frappe.throw("Check-out date must be after check-in date")
        
        # Build filters
        filters = {"status": ["!=", "Inactive"]}
        if accommodation_id:
            filters["name"] = accommodation_id
        
        # Get accommodations
        accommodations = frappe.get_all(
            "Accommodation",
            fields=[
                "name",
                "accommodation_name",
                "location", 
                "accommodation_capacity",
                "accommodation_occupancy"
            ],
            filters=filters,
            order_by="accommodation_name asc"
        )
        
        availability_data = []
        
        for acc in accommodations:
            # Calculate available capacity
            available_capacity = acc.accommodation_capacity - acc.accommodation_occupancy
            
            # Get rooms with availability
            available_rooms = frappe.get_all(
                "Room",
                fields=["name", "room_number", "room_capacity", "status"],
                filters={
                    "accommodation": acc.name,
                    "status": ["in", ["Available", "Partially Occupied"]]
                },
                order_by="room_number asc"
            )
            
            availability_data.append({
                "accommodation_id": acc.name,
                "accommodation_name": acc.accommodation_name,
                "location": acc.location,
                "total_capacity": acc.accommodation_capacity,
                "current_occupancy": acc.accommodation_occupancy,
                "available_capacity": available_capacity,
                "available_rooms": len(available_rooms),
                "rooms": available_rooms[:5]  # Limit to first 5 rooms
            })
        
        return {
            "availability": availability_data,
            "search_criteria": {
                "accommodation_id": accommodation_id,
                "check_in_date": str(check_in_date) if check_in_date else None,
                "check_out_date": str(check_out_date) if check_out_date else None
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error checking availability: {str(e)}")
        return {"availability": [], "search_criteria": {}}