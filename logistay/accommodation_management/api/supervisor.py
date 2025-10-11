import frappe
from frappe.utils import getdate, now
import re


@frappe.whitelist()
def get_supervisor_tasks(supervisor_id=None, status=None, date_from=None, date_to=None):
    """Get supervisor daily tasks (requires authentication)"""
    try:
        # Check authentication
        if frappe.session.user == "Guest":
            frappe.throw("Authentication required")
        
        # Validate supervisor access
        user_roles = frappe.get_roles(frappe.session.user)
        if not any(role in ["Accommodation Supervisor", "Accommodation Manager", "System Manager"] for role in user_roles):
            frappe.throw("Insufficient permissions")
        
        # Build filters
        filters = {}
        
        if supervisor_id:
            if not re.match(r'^[a-zA-Z0-9\-_]{1,50}$', supervisor_id):
                frappe.throw("Invalid supervisor ID")
            filters["supervisor"] = supervisor_id
        else:
            # If no supervisor specified, get current user's tasks
            current_employee = frappe.get_value("Employee", {"user_id": frappe.session.user}, "name")
            if current_employee:
                filters["supervisor"] = current_employee
        
        if status and status in ["Pending", "In Progress", "Completed", "Overdue"]:
            if status == "Overdue":
                filters["due_date"] = ["<", getdate()]
                filters["completion_status"] = ["!=", "Satisfactory"]
            else:
                filters["completion_status"] = status
        
        if date_from:
            try:
                date_from = getdate(date_from)
                filters["task_date"] = [">=", date_from]
            except:
                frappe.throw("Invalid date_from format")
        
        if date_to:
            try:
                date_to = getdate(date_to)
                if "task_date" in filters:
                    filters["task_date"] = ["between", [date_from, date_to]]
                else:
                    filters["task_date"] = ["<=", date_to]
            except:
                frappe.throw("Invalid date_to format")
        
        # Get tasks
        tasks = frappe.get_all(
            "Supervisor Daily Task",
            fields=[
                "name",
                "task_description",
                "supervisor",
                "supervisor_name", 
                "accommodation",
                "room",
                "task_date",
                "due_date",
                "priority",
                "completion_status",
                "completed_date",
                "completion_notes"
            ],
            filters=filters,
            order_by="task_date desc, priority desc",
            limit=50
        )
        
        # Enrich task data
        enriched_tasks = []
        for task in tasks:
            # Get accommodation name
            acc_name = frappe.get_value("Accommodation", task["accommodation"], "accommodation_name") if task["accommodation"] else None
            
            # Get room number
            room_number = frappe.get_value("Room", task["room"], "room_number") if task["room"] else None
            
            # Determine status
            task_status = task["completion_status"] or "Pending"
            if task_status != "Satisfactory" and task["due_date"]:
                if getdate(task["due_date"]) < getdate():
                    task_status = "Overdue"
            
            enriched_tasks.append({
                "task_id": task["name"],
                "description": task["task_description"],
                "supervisor": task["supervisor_name"] or task["supervisor"],
                "accommodation_name": acc_name,
                "room_number": room_number,
                "task_date": task["task_date"],
                "due_date": task["due_date"],
                "priority": task["priority"],
                "status": task_status,
                "completed_date": task["completed_date"],
                "completion_notes": task["completion_notes"]
            })
        
        return {
            "tasks": enriched_tasks,
            "total_count": len(enriched_tasks),
            "filters_applied": {
                "supervisor_id": supervisor_id,
                "status": status,
                "date_from": str(date_from) if date_from else None,
                "date_to": str(date_to) if date_to else None
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting supervisor tasks: {str(e)}")
        frappe.throw("Failed to load supervisor tasks")


@frappe.whitelist()
def get_task_statistics(supervisor_id=None):
    """Get task statistics for supervisor dashboard (requires authentication)"""
    try:
        # Check authentication
        if frappe.session.user == "Guest":
            frappe.throw("Authentication required")
        
        # Validate supervisor access
        user_roles = frappe.get_roles(frappe.session.user)
        if not any(role in ["Accommodation Supervisor", "Accommodation Manager", "System Manager"] for role in user_roles):
            frappe.throw("Insufficient permissions")
        
        # Build base filters
        base_filters = {}
        if supervisor_id:
            if not re.match(r'^[a-zA-Z0-9\-_]{1,50}$', supervisor_id):
                frappe.throw("Invalid supervisor ID")
            base_filters["supervisor"] = supervisor_id
        else:
            # Get current user's employee record
            current_employee = frappe.get_value("Employee", {"user_id": frappe.session.user}, "name")
            if current_employee:
                base_filters["supervisor"] = current_employee
        
        today = getdate()
        
        # Get various task counts
        stats = {
            "total_tasks": frappe.db.count("Supervisor Daily Task", base_filters),
            "pending_tasks": frappe.db.count("Supervisor Daily Task", {
                **base_filters,
                "completion_status": ["in", ["Pending", "In Progress"]]
            }),
            "completed_tasks": frappe.db.count("Supervisor Daily Task", {
                **base_filters,
                "completion_status": "Satisfactory"
            }),
            "overdue_tasks": frappe.db.count("Supervisor Daily Task", {
                **base_filters,
                "due_date": ["<", today],
                "completion_status": ["!=", "Satisfactory"]
            }),
            "today_tasks": frappe.db.count("Supervisor Daily Task", {
                **base_filters,
                "task_date": today
            }),
            "high_priority_pending": frappe.db.count("Supervisor Daily Task", {
                **base_filters,
                "priority": "High",
                "completion_status": ["in", ["Pending", "In Progress"]]
            })
        }
        
        return stats
        
    except Exception as e:
        frappe.log_error(f"Error getting task statistics: {str(e)}")
        return {
            "total_tasks": 0,
            "pending_tasks": 0, 
            "completed_tasks": 0,
            "overdue_tasks": 0,
            "today_tasks": 0,
            "high_priority_pending": 0
        }