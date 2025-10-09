"""
Fleet Access Log DocType Controller
Handles audit trail and access logging functionality
"""

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, get_datetime
from typing import Dict, Any


class FleetAccessLog(Document):
    """Fleet Access Log document controller"""
    
    def before_insert(self):
        """Set default values before inserting"""
        if not self.timestamp:
            self.timestamp = now_datetime()
        
        if not self.session_id and frappe.session:
            self.session_id = frappe.session.sid
        
        # Set IP address if not provided
        if not self.ip_address and frappe.local.request_ip:
            self.ip_address = frappe.local.request_ip
        
        # Set user agent if not provided
        if not self.user_agent and frappe.local.request:
            self.user_agent = frappe.local.request.headers.get("User-Agent", "Unknown")
    
    def validate(self):
        """Validate the access log entry"""
        # Ensure required fields are set
        if not self.user:
            frappe.throw("User is required")
        
        if not self.document_type:
            frappe.throw("Document Type is required")
        
        if not self.action:
            frappe.throw("Action is required")
        
        # Validate timestamp
        if self.timestamp and get_datetime(self.timestamp) > now_datetime():
            frappe.throw("Timestamp cannot be in the future")
    
    def on_update(self):
        """Handle post-update operations"""
        # Clean up old logs if needed
        self.cleanup_old_logs()
    
    def cleanup_old_logs(self):
        """Clean up old access logs based on retention policy"""
        try:
            # Get retention settings from system settings
            retention_days = frappe.db.get_single_value("Fleet Settings", "access_log_retention_days") or 90
            
            # Delete logs older than retention period
            cutoff_date = frappe.utils.add_days(now_datetime(), -retention_days)
            
            old_logs = frappe.get_all(
                "Fleet Access Log",
                filters={"timestamp": ["<", cutoff_date]},
                limit=1000  # Process in batches
            )
            
            if old_logs:
                for log in old_logs:
                    frappe.delete_doc("Fleet Access Log", log.name, ignore_permissions=True)
                
                frappe.db.commit()
                
        except Exception as e:
            frappe.log_error(f"Error cleaning up access logs: {str(e)}", "Access Log Cleanup")
    
    @staticmethod
    def log_access(user: str, document_type: str, document_name: str, action: str, 
                   success: bool = True, error_message: str = None, 
                   additional_info: Dict[str, Any] = None):
        """Static method to create access log entries"""
        try:
            log_doc = frappe.get_doc({
                "doctype": "Fleet Access Log",
                "user": user,
                "document_type": document_type,
                "document_name": document_name,
                "action": action,
                "success": success,
                "error_message": error_message,
                "additional_info": additional_info
            })
            
            log_doc.insert(ignore_permissions=True)
            frappe.db.commit()
            
        except Exception as e:
            # Don't let logging errors break the main functionality
            frappe.log_error(f"Failed to create access log: {str(e)}", "Access Log Error")
    
    @staticmethod
    def get_user_activity_summary(user: str, days: int = 30) -> Dict[str, Any]:
        """Get user activity summary for the specified period"""
        from_date = frappe.utils.add_days(now_datetime(), -days)
        
        # Get total access count
        total_access = frappe.db.count(
            "Fleet Access Log",
            filters={"user": user, "timestamp": [">=", from_date]}
        )
        
        # Get successful vs failed attempts
        successful_access = frappe.db.count(
            "Fleet Access Log",
            filters={"user": user, "timestamp": [">=", from_date], "success": 1}
        )
        
        failed_access = total_access - successful_access
        
        # Get most accessed document types
        document_types = frappe.db.sql("""
            SELECT document_type, COUNT(*) as count
            FROM `tabFleet Access Log`
            WHERE user = %s AND timestamp >= %s
            GROUP BY document_type
            ORDER BY count DESC
            LIMIT 10
        """, (user, from_date), as_dict=True)
        
        # Get most common actions
        actions = frappe.db.sql("""
            SELECT action, COUNT(*) as count
            FROM `tabFleet Access Log`
            WHERE user = %s AND timestamp >= %s
            GROUP BY action
            ORDER BY count DESC
            LIMIT 10
        """, (user, from_date), as_dict=True)
        
        # Get daily activity
        daily_activity = frappe.db.sql("""
            SELECT DATE(timestamp) as date, COUNT(*) as count
            FROM `tabFleet Access Log`
            WHERE user = %s AND timestamp >= %s
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        """, (user, from_date), as_dict=True)
        
        return {
            "user": user,
            "period_days": days,
            "total_access": total_access,
            "successful_access": successful_access,
            "failed_access": failed_access,
            "success_rate": (successful_access / total_access * 100) if total_access > 0 else 0,
            "document_types": document_types,
            "actions": actions,
            "daily_activity": daily_activity
        }
    
    @staticmethod
    def get_security_alerts(days: int = 7) -> list:
        """Get security alerts based on access patterns"""
        from_date = frappe.utils.add_days(now_datetime(), -days)
        alerts = []
        
        # Check for multiple failed login attempts
        failed_attempts = frappe.db.sql("""
            SELECT user, COUNT(*) as count, MAX(timestamp) as last_attempt
            FROM `tabFleet Access Log`
            WHERE success = 0 AND timestamp >= %s
            GROUP BY user
            HAVING count >= 5
            ORDER BY count DESC
        """, (from_date,), as_dict=True)
        
        for attempt in failed_attempts:
            alerts.append({
                "type": "Multiple Failed Attempts",
                "user": attempt.user,
                "count": attempt.count,
                "last_attempt": attempt.last_attempt,
                "severity": "High" if attempt.count >= 10 else "Medium"
            })
        
        # Check for unusual access patterns (access outside normal hours)
        unusual_access = frappe.db.sql("""
            SELECT user, document_type, timestamp
            FROM `tabFleet Access Log`
            WHERE timestamp >= %s 
            AND (HOUR(timestamp) < 6 OR HOUR(timestamp) > 22)
            AND success = 1
            ORDER BY timestamp DESC
            LIMIT 50
        """, (from_date,), as_dict=True)
        
        for access in unusual_access:
            alerts.append({
                "type": "Unusual Access Time",
                "user": access.user,
                "document_type": access.document_type,
                "timestamp": access.timestamp,
                "severity": "Low"
            })
        
        # Check for bulk data exports
        bulk_exports = frappe.db.sql("""
            SELECT user, COUNT(*) as count, DATE(timestamp) as date
            FROM `tabFleet Access Log`
            WHERE action = 'Export' AND timestamp >= %s
            GROUP BY user, DATE(timestamp)
            HAVING count >= 10
            ORDER BY count DESC
        """, (from_date,), as_dict=True)
        
        for export in bulk_exports:
            alerts.append({
                "type": "Bulk Data Export",
                "user": export.user,
                "count": export.count,
                "date": export.date,
                "severity": "Medium"
            })
        
        return alerts


# Utility functions for access logging
def log_document_access(doc, method):
    """Hook function to log document access"""
    if frappe.session.user == "Guest":
        return
    
    FleetAccessLog.log_access(
        user=frappe.session.user,
        document_type=doc.doctype,
        document_name=doc.name,
        action=method.title(),
        success=True
    )


def log_failed_access(doctype: str, doc_name: str, action: str, error: str):
    """Log failed access attempts"""
    if frappe.session.user == "Guest":
        return
    
    FleetAccessLog.log_access(
        user=frappe.session.user,
        document_type=doctype,
        document_name=doc_name,
        action=action,
        success=False,
        error_message=error
    )