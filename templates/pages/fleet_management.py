import frappe

def get_context(context):
    """Get context for fleet management dashboard page"""
    context.no_cache = 1
    context.title = "Fleet Management Dashboard - LogiStay"
    context.description = "Fleet Management Dashboard for LogiStay Fleet Management System"
    context.keywords = "fleet, management, dashboard, vehicles, drivers"
    
    return context