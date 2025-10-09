import frappe

def update_workspace():
    try:
        # Get the Fleet Management workspace
        workspace = frappe.get_doc("Workspace", "Fleet Management")

        # Define the new content structure
        new_content = [
            {"id": "fleet_ops_shortcuts", "type": "shortcut", "data": {"shortcut_name": "Fleet Vehicle", "col": 3}},
            {"id": "fleet_driver_shortcut", "type": "shortcut", "data": {"shortcut_name": "Fleet Driver", "col": 3}},
            {"id": "fuel_entry_shortcut", "type": "shortcut", "data": {"shortcut_name": "Fuel Entry", "col": 3}},
            {"id": "assignment_shortcut", "type": "shortcut", "data": {"shortcut_name": "Driver Vehicle Assignment", "col": 3}},
            {"id": "spacer1", "type": "spacer", "data": {"col": 12}},
            {"id": "fleet_ops_card", "type": "card", "data": {"card_name": "Fleet Operations", "col": 4}},
            {"id": "fleet_records_card", "type": "card", "data": {"card_name": "Fleet Records", "col": 4}},
            {"id": "supplier_card", "type": "card", "data": {"card_name": "Suppliers", "col": 4}},
            {"id": "fleet_reports_card", "type": "card", "data": {"card_name": "Fleet Reports", "col": 4}},
            {"id": "fleet_settings_card", "type": "card", "data": {"card_name": "Fleet Settings", "col": 4}}
        ]

        # Update the content field
        workspace.content = frappe.as_json(new_content)

        # Save the workspace
        workspace.save(ignore_permissions=True)
        frappe.db.commit()
        print("Workspace 'Fleet Management' updated successfully.")

    except frappe.DoesNotExistError:
        print("Workspace 'Fleet Management' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the function
update_workspace()