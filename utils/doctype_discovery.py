import frappe
import json
from frappe.model.meta import get_meta
from frappe import utils


def get_app_doctypes(app_name="logistay"):
    """
    Auto-discover all DocTypes in the Fleet Management app
    Returns a JSON inventory with doctype names, key fields, and primary actions
    """
    try:
        # Get all DocTypes for the app
        doctypes = frappe.get_all(
            "DocType",
            filters={"module": ["like", "%Fleet%"], "custom": 0},
            fields=["name", "module", "is_submittable", "track_changes", "has_web_view"]
        )
        
        inventory = {}
        
        for doctype_info in doctypes:
            doctype_name = doctype_info.name
            
            try:
                # Get DocType metadata
                meta = get_meta(doctype_name)
                
                # Extract key fields
                key_fields = []
                for field in meta.fields:
                    if field.fieldtype in ["Data", "Link", "Select", "Date", "Datetime", "Currency", "Float", "Int"]:
                        if field.in_list_view or field.reqd or field.bold:
                            key_fields.append({
                                "fieldname": field.fieldname,
                                "label": field.label,
                                "fieldtype": field.fieldtype,
                                "options": field.options if field.options else None,
                                "required": field.reqd,
                                "read_only": field.read_only
                            })
                
                # Determine primary actions based on DocType properties
                primary_actions = ["view", "list"]
                if meta.permissions:
                    for perm in meta.permissions:
                        if perm.role in ["Fleet Driver", "Fleet Manager", "System Manager"]:
                            if perm.create:
                                primary_actions.append("create")
                            if perm.write:
                                primary_actions.append("edit")
                            if perm.delete:
                                primary_actions.append("delete")
                            if perm.submit and doctype_info.is_submittable:
                                primary_actions.append("submit")
                
                # Driver-relevant workflows
                driver_workflows = []
                if "driver" in doctype_name.lower():
                    driver_workflows = ["view_profile", "update_status", "view_assignments"]
                elif "vehicle" in doctype_name.lower():
                    driver_workflows = ["view_assigned_vehicle", "report_issue"]
                elif "fuel" in doctype_name.lower():
                    driver_workflows = ["create_entry", "upload_receipt", "view_history"]
                elif "shift" in doctype_name.lower():
                    driver_workflows = ["start_shift", "end_shift", "view_earnings"]
                elif "assignment" in doctype_name.lower():
                    driver_workflows = ["accept_assignment", "view_details", "update_status"]
                
                inventory[doctype_name] = {
                    "module": doctype_info.module,
                    "is_submittable": doctype_info.is_submittable,
                    "track_changes": doctype_info.track_changes,
                    "has_web_view": doctype_info.has_web_view,
                    "key_fields": key_fields[:10],  # Limit to top 10 fields
                    "primary_actions": list(set(primary_actions)),
                    "driver_workflows": driver_workflows,
                    "driver_relevance": calculate_driver_relevance(doctype_name, key_fields)
                }
                
            except Exception as e:
                frappe.log_error(f"Error processing DocType {doctype_name}: {str(e)}")
                continue
        
        return inventory
        
    except Exception as e:
        frappe.log_error(f"Error in doctype discovery: {str(e)}")
        return {}


def calculate_driver_relevance(doctype_name, key_fields):
    """
    Calculate how relevant a DocType is for driver self-service
    Returns a score from 0-10
    """
    score = 0
    
    # DocType name relevance
    driver_keywords = ["driver", "fuel", "shift", "assignment", "vehicle", "trip"]
    for keyword in driver_keywords:
        if keyword in doctype_name.lower():
            score += 2
    
    # Field relevance
    driver_field_keywords = ["driver", "vehicle", "fuel", "shift", "assignment", "trip", "earnings"]
    for field in key_fields:
        for keyword in driver_field_keywords:
            if keyword in field.get("fieldname", "").lower() or keyword in field.get("label", "").lower():
                score += 1
    
    return min(score, 10)  # Cap at 10


@frappe.whitelist()
def get_driver_relevant_doctypes():
    """
    Get DocTypes most relevant for driver self-service
    Whitelisted method for API access
    """
    inventory = get_app_doctypes()
    
    # Filter and sort by driver relevance
    relevant_doctypes = {}
    for doctype_name, info in inventory.items():
        if info["driver_relevance"] >= 3:  # Only include highly relevant DocTypes
            relevant_doctypes[doctype_name] = info
    
    # Sort by relevance score
    sorted_doctypes = dict(sorted(
        relevant_doctypes.items(), 
        key=lambda x: x[1]["driver_relevance"], 
        reverse=True
    ))
    
    return {
        "total_doctypes": len(inventory),
        "driver_relevant_count": len(sorted_doctypes),
        "doctypes": sorted_doctypes,
        "generated_at": utils.now()
    }


def generate_inventory_json():
    """
    Generate and save the DocType inventory as JSON file
    """
    inventory = get_driver_relevant_doctypes()
    
    # Save to public folder for easy access
    file_path = frappe.get_app_path("logistay", "public", "driver_ss", "doctype_inventory.json")
    
    try:
        import os
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(inventory, f, indent=2, default=str)
        
        return file_path
    except Exception as e:
        frappe.log_error(f"Error saving inventory JSON: {str(e)}")
        return None


if __name__ == "__main__":
    # For testing purposes
    inventory = get_driver_relevant_doctypes()
    print(json.dumps(inventory, indent=2, default=str))