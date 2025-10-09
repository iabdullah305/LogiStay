"""
Role-Based Access Control System for Fleet Management
Handles permissions, data filtering, and security policies
"""

import frappe
from frappe import _
from frappe.permissions import has_permission
from frappe.utils import now_datetime, get_datetime
import json
from typing import Dict, List, Optional, Any


class RolePermissionManager:
    """Manages role-based permissions and access control"""
    
    def __init__(self):
        self.role_hierarchy = {
            "System Manager": 100,
            "Fleet Manager": 80,
            "Fleet Supervisor": 60,
            "Project Manager": 50,
            "Fleet Driver": 20,
            "Fleet Viewer": 10
        }
    
    def get_user_role_level(self, user: Optional[str] = None) -> int:
        """Get the highest role level for a user"""
        if not user:
            user = frappe.session.user
        
        user_roles = frappe.get_roles(user)
        max_level = 0
        
        for role in user_roles:
            if role in self.role_hierarchy:
                max_level = max(max_level, self.role_hierarchy[role])
        
        return max_level
    
    def can_access_document(self, doctype: str, doc_name: str, user: Optional[str] = None) -> bool:
        """Check if user can access a specific document"""
        if not user:
            user = frappe.session.user
        
        # System Manager has access to everything
        if "System Manager" in frappe.get_roles(user):
            return True
        
        doc = frappe.get_doc(doctype, doc_name)
        user_roles = frappe.get_roles(user)
        
        # Apply role-specific filters
        if "Fleet Driver" in user_roles:
            return self._check_driver_access(doc, user)
        elif "Project Manager" in user_roles:
            return self._check_project_manager_access(doc, user)
        elif "Fleet Supervisor" in user_roles:
            return self._check_supervisor_access(doc, user)
        
        return has_permission(doctype, "read", doc_name, user=user)
    
    def _check_driver_access(self, doc, user: str) -> bool:
        """Check driver-specific access permissions"""
        driver_doc = frappe.get_value("Fleet Driver", {"user": user}, "name")
        
        if doc.doctype == "Fleet Shift":
            return doc.assigned_driver == driver_doc
        elif doc.doctype == "Fuel Entry":
            return doc.driver == driver_doc
        elif doc.doctype == "Fleet Driver":
            return doc.name == driver_doc
        
        return False
    
    def _check_project_manager_access(self, doc, user: str) -> bool:
        """Check project manager-specific access permissions"""
        user_projects = frappe.get_all("Fleet Project", 
                                     filters={"project_manager": user}, 
                                     pluck="name")
        
        if hasattr(doc, "project") and doc.project:
            return doc.project in user_projects
        
        return True  # Allow access to non-project specific documents
    
    def _check_supervisor_access(self, doc, user: str) -> bool:
        """Check supervisor-specific access permissions"""
        supervisor_branches = frappe.get_all("Fleet Branch", 
                                           filters={"supervisor": user}, 
                                           pluck="name")
        
        if hasattr(doc, "branch") and doc.branch:
            return doc.branch in supervisor_branches
        
        return True
    
    def get_filtered_query(self, doctype: str, user: str = None) -> Dict[str, Any]:
        """Get filtered query conditions based on user role"""
        if not user:
            user = frappe.session.user
        
        user_roles = frappe.get_roles(user)
        filters = {}
        
        # System Manager and Fleet Manager see everything
        if any(role in ["System Manager", "Fleet Manager"] for role in user_roles):
            return filters
        
        # Fleet Driver sees only their own records
        if "Fleet Driver" in user_roles:
            driver_doc = frappe.get_value("Fleet Driver", {"user": user}, "name")
            if doctype == "Fleet Shift":
                filters["assigned_driver"] = driver_doc
            elif doctype == "Fuel Entry":
                filters["driver"] = driver_doc
            elif doctype == "Fleet Driver":
                filters["name"] = driver_doc
        
        # Project Manager sees only their projects
        elif "Project Manager" in user_roles:
            user_projects = frappe.get_all("Fleet Project", 
                                         filters={"project_manager": user}, 
                                         pluck="name")
            if hasattr(frappe.get_meta(doctype), "project"):
                filters["project"] = ["in", user_projects]
        
        # Fleet Supervisor sees their branches
        elif "Fleet Supervisor" in user_roles:
            supervisor_branches = frappe.get_all("Fleet Branch", 
                                               filters={"supervisor": user}, 
                                               pluck="name")
            if hasattr(frappe.get_meta(doctype), "branch"):
                filters["branch"] = ["in", supervisor_branches]
        
        return filters
    
    def validate_field_permissions(self, doc, user: str = None) -> List[str]:
        """Get list of restricted fields for user role"""
        if not user:
            user = frappe.session.user
        
        user_roles = frappe.get_roles(user)
        restricted_fields = []
        
        # Load role configuration
        role_config = self._get_role_config(user_roles)
        
        if doc.doctype in role_config.get("field_restrictions", {}):
            field_restrictions = role_config["field_restrictions"][doc.doctype]
            restricted_fields = field_restrictions.get("restricted_fields", [])
        
        return restricted_fields
    
    def _get_role_config(self, user_roles: List[str]) -> Dict[str, Any]:
        """Load role configuration from JSON files"""
        config = {"field_restrictions": {}, "workflow_restrictions": {}}
        
        for role in user_roles:
            if role in self.role_hierarchy:
                role_file = f"shift_scheduling/logistay/roles/{role.lower().replace(' ', '_')}.json"
                try:
                    with open(frappe.get_app_path("shift_scheduling", role_file)) as f:
                        role_data = json.load(f)
                        if "restrictions" in role_data:
                            config.update(role_data["restrictions"])
                except FileNotFoundError:
                    continue
        
        return config
    
    def check_approval_permissions(self, doctype: str, amount: float = 0, user: str = None) -> Dict[str, Any]:
        """Check if user can approve documents and within what limits"""
        if not user:
            user = frappe.session.user
        
        user_roles = frappe.get_roles(user)
        approval_info = {
            "can_approve": False,
            "approval_limit": 0,
            "requires_higher_approval": False
        }
        
        role_config = self._get_role_config(user_roles)
        workflow_restrictions = role_config.get("workflow_restrictions", {})
        
        # Check approval permissions based on document type
        if doctype == "Fleet Shift":
            approval_info["can_approve"] = workflow_restrictions.get("can_approve_shifts", False)
        elif doctype == "Fuel Entry":
            approval_info["can_approve"] = workflow_restrictions.get("can_approve_fuel_entries", False)
        elif doctype == "Cost Calculation Engine":
            approval_info["can_approve"] = workflow_restrictions.get("can_approve_cost_calculations", False)
        
        # Check amount limits
        approval_limit = workflow_restrictions.get("approval_limit", 0)
        requires_approval_above = workflow_restrictions.get("requires_approval_above", 0)
        
        approval_info["approval_limit"] = approval_limit
        approval_info["requires_higher_approval"] = amount > approval_limit
        
        return approval_info
    
    def log_access_attempt(self, doctype: str, doc_name: str, action: str, success: bool, user: str = None):
        """Log access attempts for audit trail"""
        if not user:
            user = frappe.session.user
        
        audit_log = frappe.get_doc({
            "doctype": "Fleet Access Log",
            "user": user,
            "document_type": doctype,
            "document_name": doc_name,
            "action": action,
            "success": success,
            "timestamp": now_datetime(),
            "ip_address": frappe.local.request_ip if frappe.local.request_ip else "Unknown",
            "user_agent": frappe.local.request.headers.get("User-Agent", "Unknown") if frappe.local.request else "Unknown"
        })
        
        try:
            audit_log.insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Failed to log access attempt: {str(e)}", "Access Log Error")
    
    def validate_session_security(self, user: str = None) -> Dict[str, Any]:
        """Validate session security based on role restrictions"""
        if not user:
            user = frappe.session.user
        
        user_roles = frappe.get_roles(user)
        role_config = self._get_role_config(user_roles)
        security_settings = role_config.get("security_settings", {})
        
        validation_result = {
            "valid": True,
            "messages": [],
            "actions_required": []
        }
        
        # Check session timeout
        session_timeout = security_settings.get("session_timeout", 480)  # Default 8 hours
        if frappe.session.data.get("last_activity"):
            last_activity = get_datetime(frappe.session.data["last_activity"])
            if (now_datetime() - last_activity).total_seconds() > (session_timeout * 60):
                validation_result["valid"] = False
                validation_result["messages"].append("Session expired due to inactivity")
                validation_result["actions_required"].append("re_login")
        
        # Check time restrictions
        time_restrictions = security_settings.get("time_restrictions", {})
        if time_restrictions:
            current_time = now_datetime()
            allowed_hours = time_restrictions.get("allowed_hours", "00:00-23:59")
            allowed_days = time_restrictions.get("allowed_days", [])
            
            # Validate time range
            start_time, end_time = allowed_hours.split("-")
            current_hour_min = current_time.strftime("%H:%M")
            
            if not (start_time <= current_hour_min <= end_time):
                validation_result["valid"] = False
                validation_result["messages"].append(f"Access not allowed at this time. Allowed hours: {allowed_hours}")
            
            # Validate day of week
            if allowed_days and current_time.strftime("%A") not in allowed_days:
                validation_result["valid"] = False
                validation_result["messages"].append(f"Access not allowed on {current_time.strftime('%A')}")
        
        return validation_result


# Utility functions for permission checks
def has_fleet_permission(doctype: str, ptype: str, doc_name: str = None, user: str = None) -> bool:
    """Enhanced permission check for fleet documents"""
    permission_manager = RolePermissionManager()
    
    if doc_name:
        return permission_manager.can_access_document(doctype, doc_name, user)
    
    return has_permission(doctype, ptype, user=user)


def get_fleet_query_conditions(doctype: str, user: str = None) -> str:
    """Get query conditions for fleet document filtering"""
    permission_manager = RolePermissionManager()
    filters = permission_manager.get_filtered_query(doctype, user)
    
    conditions = []
    for field, value in filters.items():
        if isinstance(value, list) and value[0] == "in":
            conditions.append(f"`tab{doctype}`.`{field}` IN ({','.join(['%s'] * len(value[1]))})")
        else:
            conditions.append(f"`tab{doctype}`.`{field}` = %s")
    
    return " AND ".join(conditions) if conditions else ""


def validate_fleet_document_access(doc, method):
    """Validate document access on save/submit"""
    permission_manager = RolePermissionManager()
    
    # Log access attempt
    permission_manager.log_access_attempt(
        doc.doctype, 
        doc.name, 
        method, 
        True
    )
    
    # Validate field permissions
    restricted_fields = permission_manager.validate_field_permissions(doc)
    
    for field in restricted_fields:
        if hasattr(doc, field) and doc.get(field):
            frappe.throw(_(f"You don't have permission to modify field: {field}"))
    
    # Validate approval permissions for submitted documents
    if method in ["submit", "cancel"] and hasattr(doc, "total_cost"):
        approval_info = permission_manager.check_approval_permissions(
            doc.doctype, 
            float(doc.total_cost or 0)
        )
        
        if not approval_info["can_approve"]:
            frappe.throw(_("You don't have permission to approve this document"))
        
        if approval_info["requires_higher_approval"]:
            frappe.throw(_(f"Amount exceeds your approval limit of {approval_info['approval_limit']}"))


def validate_session_security():
    """Validate session security on each request"""
    if frappe.session.user == "Guest":
        return
    
    permission_manager = RolePermissionManager()
    validation_result = permission_manager.validate_session_security()
    
    if not validation_result["valid"]:
        for message in validation_result["messages"]:
            frappe.throw(_(message))