import frappe

def execute(filters=None):
    columns = [
        {"label": "Driver", "fieldname": "name", "fieldtype": "Link", "options": "Fleet Driver", "width": 200},
        {"label": "First Name", "fieldname": "first_name", "fieldtype": "Data", "width": 150},
        {"label": "Last Name", "fieldname": "last_name", "fieldtype": "Data", "width": 150},
        {"label": "License Number", "fieldname": "license_number", "fieldtype": "Data", "width": 150},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
    ]

    data = frappe.get_all(
        "Fleet Driver",
        fields=["name", "first_name", "last_name", "license_number", "status"],
        filters=filters,
        order_by="name asc"
    )

    return columns, data