import frappe
import json
import os

def after_install():
    """
    Called after LogiStay app installation
    Sets up workspaces and initial configuration
    """
    try:
        print("🚀 Setting up LogiStay workspaces...")
        
        # Create Fleet Management Workspace
        create_workspace_from_file(
            workspace_name="Fleet Management",
            file_path="fleet_management/workspace/fleet_management.json"
        )
        
        # Create Accommodation Management Workspace
        create_workspace_from_file(
            workspace_name="Accommodation Management", 
            file_path="accommodation_management/workspace/accommodation_management.json"
        )
        
        frappe.db.commit()
        print("✅ LogiStay workspaces setup completed successfully!")
        
    except Exception as e:
        frappe.log_error(f"Error in LogiStay after_install: {str(e)}")
        print(f"❌ Error setting up LogiStay: {str(e)}")

def create_workspace_from_file(workspace_name, file_path):
    """
    Create workspace from JSON file
    
    Args:
        workspace_name (str): Name of the workspace
        file_path (str): Relative path to workspace JSON file within app
    """
    try:
        # Check if workspace already exists
        if frappe.db.exists("Workspace", workspace_name):
            print(f"Workspace '{workspace_name}' already exists, skipping...")
            return
        
        # Get app path and construct full file path
        app_path = frappe.get_app_path("logistay")
        full_file_path = os.path.join(app_path, file_path)
        
        if not os.path.exists(full_file_path):
            print(f"❌ Workspace file not found: {full_file_path}")
            return
        
        # Load workspace data from JSON file
        with open(full_file_path, 'r', encoding='utf-8') as f:
            workspace_data = json.load(f)
        
        # Create new workspace document
        workspace_doc = frappe.new_doc("Workspace")
        
        # Update with data from JSON file
        for key, value in workspace_data.items():
            if hasattr(workspace_doc, key):
                setattr(workspace_doc, key, value)
        
        # Insert the workspace
        workspace_doc.insert(ignore_permissions=True)
        
        print(f"✅ Created workspace: {workspace_name}")
        
    except Exception as e:
        frappe.log_error(f"Error creating workspace {workspace_name}: {str(e)}")
        print(f"❌ Error creating workspace {workspace_name}: {str(e)}")

def setup_default_permissions():
    """
    Setup default permissions for LogiStay doctypes
    """
    # This can be expanded to set up role permissions
    pass