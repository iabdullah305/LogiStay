import frappe

def get_context(context):
    """Context for the Vue SPA app page"""
    context.no_cache = 1
    context.title = "LogiStay Fleet Management"
    
    # Set meta tags for SEO
    context.metatags = {
        "description": "LogiStay Fleet and Accommodation Management System",
        "keywords": "fleet management, accommodation, logistics, vehicle tracking",
        "og:title": "LogiStay Fleet Management",
        "og:description": "Comprehensive fleet and accommodation management solution",
        "og:type": "website"
    }
    
    return context