import frappe
from logistay.utils.workspace_template import upsert_workspace, get_logistay_blocks

def execute():
    """
    Patch to create Fleet Management workspace
    """
    try:
        # Create Fleet Management workspace
        result = upsert_workspace(
            title="Fleet Management",
            module="Fleet Management", 
            route="fleet-management",
            blocks=get_logistay_blocks(),
            force_replace=True,
            dry_run=False
        )
        
        if result.get("ok"):
            frappe.logger().info(f"Fleet Management workspace created successfully: {result.get('messages')}")
        else:
            frappe.logger().error(f"Failed to create Fleet Management workspace: {result.get('messages')}")
            
    except Exception as e:
        frappe.logger().error(f"Error creating Fleet Management workspace: {str(e)}")
        # Don't raise exception to prevent patch failure
        pass