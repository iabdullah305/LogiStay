import frappe

def get_context(context):
    """Get context for driver dashboard page"""
    context.no_cache = 1
    context.title = "Driver Dashboard - LogiStay"
    context.description = "Driver Dashboard for LogiStay Fleet Management System"
    context.keywords = "driver, dashboard, fleet, management, trips"
    
    # Check if user is logged in
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect
    
    return context