frappe.query_reports["Fuel Expense Report"] = {
    "filters": [
        {
            "fieldname": "date_range",
            "label": __("Date Range"),
            "fieldtype": "DateRange",
            "default": [frappe.datetime.add_months(frappe.datetime.now_date(), -1), frappe.datetime.now_date()],
            "reqd": 1
        },
        {
            "fieldname": "vehicle",
            "label": __("Vehicle"),
            "fieldtype": "Link",
            "options": "Fleet Vehicle"
        },
        {
            "fieldname": "driver",
            "label": __("Driver"),
            "fieldtype": "Link",
            "options": "Fleet Driver"
        }
    ]
};