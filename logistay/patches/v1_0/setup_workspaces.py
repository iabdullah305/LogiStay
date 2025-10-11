import frappe
import json
import os
from frappe.utils import get_bench_path

def execute():
    """
    Setup LogiStay Workspaces automatically
    This patch creates the required workspaces for Fleet Management and Accommodation Management
    """
    try:
        # Create Fleet Management Workspace
        create_fleet_workspace()
        
        # Create Accommodation Management Workspace  
        create_accommodation_workspace()
        
        frappe.db.commit()
        print("✅ LogiStay Workspaces created successfully!")
        
    except Exception as e:
        frappe.log_error(f"Error creating LogiStay workspaces: {str(e)}")
        print(f"❌ Error creating workspaces: {str(e)}")

def create_fleet_workspace():
    """Create Fleet Management Workspace"""
    workspace_name = "Fleet Management"
    
    # Check if workspace already exists
    if frappe.db.exists("Workspace", workspace_name):
        print(f"Workspace '{workspace_name}' already exists, skipping...")
        return
    
    # Load workspace JSON from file
    app_path = frappe.get_app_path("logistay")
    workspace_file = os.path.join(app_path, "fleet_management", "workspace", "fleet_management.json")
    
    if os.path.exists(workspace_file):
        with open(workspace_file, 'r', encoding='utf-8') as f:
            workspace_data = json.load(f)
        
        # Create workspace document
        workspace_doc = frappe.new_doc("Workspace")
        workspace_doc.update(workspace_data)
        workspace_doc.insert(ignore_permissions=True)
        
        print(f"✅ Created workspace: {workspace_name}")
    else:
        print(f"❌ Workspace file not found: {workspace_file}")

def create_accommodation_workspace():
    """Create Accommodation Management Workspace"""
    workspace_name = "Accommodation Management"
    
    # Check if workspace already exists
    if frappe.db.exists("Workspace", workspace_name):
        print(f"Workspace '{workspace_name}' already exists, skipping...")
        return
    
    # Load workspace JSON from file
    app_path = frappe.get_app_path("logistay")
    workspace_file = os.path.join(app_path, "accommodation_management", "workspace", "accommodation_management.json")
    
    if os.path.exists(workspace_file):
        with open(workspace_file, 'r', encoding='utf-8') as f:
            workspace_data = json.load(f)
        
        # Create workspace document
        workspace_doc = frappe.new_doc("Workspace")
        workspace_doc.update(workspace_data)
        workspace_doc.insert(ignore_permissions=True)
        
        print(f"✅ Created workspace: {workspace_name}")
    else:
        print(f"❌ Workspace file not found: {workspace_file}")