#!/usr/bin/env python3
"""
Script to create Fleet Management workspace
Usage: python scripts/create_workspace.py
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def create_fleet_workspace():
    """Create Fleet Management workspace"""
    try:
        import frappe
        from fleet_management.utils.workspace_template import upsert_workspace, get_fleet_management_blocks
        
        print("Creating Fleet Management workspace...")
        
        result = upsert_workspace(
            title="Fleet Management",
            module="Fleet Management",
            route="fleet-management", 
            blocks=get_fleet_management_blocks(),
            force_replace=True,
            dry_run=False
        )
        
        if result.get("ok"):
            print("✅ Fleet Management workspace created successfully!")
            for message in result.get("messages", []):
                print(f"   {message}")
        else:
            print("❌ Failed to create Fleet Management workspace:")
            for message in result.get("messages", []):
                print(f"   {message}")
                
        return result.get("ok", False)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def preview_workspace():
    """Preview workspace creation (dry run)"""
    try:
        import frappe
        from fleet_management.utils.workspace_template import upsert_workspace, get_fleet_management_blocks
        
        print("Previewing Fleet Management workspace creation...")
        
        result = upsert_workspace(
            title="Fleet Management",
            module="Fleet Management",
            route="fleet-management",
            blocks=get_fleet_management_blocks(),
            force_replace=True,
            dry_run=True
        )
        
        print("📋 Preview results:")
        for message in result.get("messages", []):
            print(f"   {message}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fleet Management Workspace Creator")
    parser.add_argument("--preview", action="store_true", help="Preview workspace creation (dry run)")
    parser.add_argument("--site", type=str, help="Frappe site name", default="afmco.sa")
    
    args = parser.parse_args()
    
    # Initialize Frappe
    try:
        import frappe
        frappe.init(site=args.site)
        frappe.connect()
        
        if args.preview:
            success = preview_workspace()
        else:
            success = create_fleet_workspace()
            
        frappe.destroy()
        
        if success:
            print("\n🎉 Operation completed successfully!")
        else:
            print("\n💥 Operation failed!")
            sys.exit(1)
            
    except ImportError:
        print("❌ Error: Frappe not found. Make sure you're running this from frappe-bench directory.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error initializing Frappe: {str(e)}")
        sys.exit(1)