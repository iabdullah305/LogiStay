import frappe

def execute(filters=None):
    columns = [
        {"label": "Vehicle", "fieldname": "name", "fieldtype": "Link", "options": "Fleet Vehicle", "width": 200},
        {"label": "Make", "fieldname": "make", "fieldtype": "Data", "width": 150},
        {"label": "Model", "fieldname": "model", "fieldtype": "Data", "width": 150},
        {"label": "Year", "fieldname": "year", "fieldtype": "Data", "width": 100},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
    ]

    data = frappe.get_all(
        "Fleet Vehicle",
        fields=["name", "make", "model", "year", "status"],
        filters=filters,
        order_by="name asc"
    )

    return columns, data