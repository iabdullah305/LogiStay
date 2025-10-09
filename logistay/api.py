import frappe
from frappe.utils import now


@frappe.whitelist()
def get_counts():
    """Return key DocType counts without writing to DB."""
    doctypes = [
        "Fleet Vehicle",
        "Fleet Driver",
        "Fuel Entry",
        "Driver Vehicle Assignment",
        "Supplier Master",
        "Supplier Contract",
    ]
    data = {"timestamp": now(), "counts": {}}
    for dt in doctypes:
        try:
            data["counts"][dt] = frappe.db.count(dt)
        except Exception:
            data["counts"][dt] = 0
    return data


@frappe.whitelist()
def fuel_entries_today(limit: int = 10):
    """Return today's Fuel Entry list (read-only)."""
    from frappe.utils import getdate
    today = getdate()
    rows = frappe.get_all(
        "Fuel Entry",
        fields=["name", "posting_date", "vehicle", "liters", "amount"],
        filters={"posting_date": today},
        limit=limit,
        order_by="posting_date desc, name desc",
    )
    return {"timestamp": now(), "items": rows}