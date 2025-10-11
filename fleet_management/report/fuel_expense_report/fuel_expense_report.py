import frappe

def execute(filters=None):
    columns = [
        {"label": "Date", "fieldname": "fuel_date", "fieldtype": "Date", "width": 120},
        {"label": "Vehicle", "fieldname": "vehicle", "fieldtype": "Link", "options": "Fleet Vehicle", "width": 150},
        {"label": "Driver", "fieldname": "driver", "fieldtype": "Link", "options": "Fleet Driver", "width": 150},
        {"label": "Fuel Quantity (Liters)", "fieldname": "quantity_liters", "fieldtype": "Float", "width": 150},
        {"label": "Price Per Liter", "fieldname": "price_per_liter", "fieldtype": "Currency", "width": 120},
        {"label": "Total Cost", "fieldname": "total_amount", "fieldtype": "Currency", "width": 120},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
    ]

    data = frappe.get_all(
        "Fuel Entry",
        fields=["fuel_date", "vehicle", "driver", "quantity_liters", "price_per_liter", "total_amount", "status"],
        filters=filters,
        order_by="fuel_date desc"
    )

    return columns, data