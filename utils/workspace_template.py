# Template: safe create/replace Workspace (Frappe v16)
# Usage (bench console):
#   from fleet_management.utils.workspace_template import upsert_workspace
#   upsert_workspace(
#       title="Fleet Management",
#       module="Fleet Management",
#       route="fleet-management",
#       blocks=[{"id":"hdr","type":"header","data":{"text":"Fleet Management","col":12}}],
#       force_replace=True,   # delete existing same-name workspace
#       dry_run=False         # set True to preview only
#   )

import json
import frappe

def upsert_workspace(
    title: str,
    module: str,
    route: str,
    blocks: list,
    force_replace: bool = False,
    dry_run: bool = False,
):
    """
    Creates or replaces a public Workspace with given title/route.
    Safe, minimal, and explicit messages. No DB writes if dry_run=True.
    """

    result = {"ok": False, "action": None, "deleted": None, "created": None, "messages": []}

    # Resolve existing by exact name or title
    existing = (
        frappe.db.exists("Workspace", {"name": title})
        or frappe.db.exists("Workspace", {"title": title})
        or frappe.db.exists("Workspace", {"route": route})
    )

    if existing and not force_replace:
        result["messages"].append(f"Workspace exists: {existing}. Set force_replace=True to replace.")
        return result

    if dry_run:
        if existing:
            result["messages"].append(f"[DRY-RUN] Would delete: {existing}")
        result["messages"].append(f"[DRY-RUN] Would create Workspace: title='{title}', route='{route}'")
        result["ok"] = True
        result["action"] = "preview"
        return result

    try:
        frappe.db.savepoint("ws_upsert_sp")

        # Delete existing (if any)
        if existing:
            frappe.delete_doc("Workspace", existing, force=True, ignore_permissions=True)
            result["deleted"] = existing
            result["messages"].append(f"Deleted existing Workspace: {existing}")

        # Create new
        ws = frappe.new_doc("Workspace")
        ws.title = title
        ws.label = title
        ws.name = title  # keep name aligned with title
        ws.module = module
        ws.public = 1
        ws.is_hidden = 0
        ws.is_standard = 1
        ws.type = "Workspace"
        ws.icon = "folder-open"
        ws.indicator_color = "blue"
        ws.route = route
        ws.content = json.dumps(blocks or [])  # must be a JSON-encoded list

        ws.insert(ignore_permissions=True)
        result["created"] = ws.name
        result["messages"].append(f"Created Workspace: {ws.name}")

        frappe.db.commit()
        frappe.clear_cache()

        result["ok"] = True
        result["action"] = "replaced" if existing else "created"
        return result

    except Exception as e:
        frappe.db.rollback(save_point="ws_upsert_sp")
        result["messages"].append(f"Error: {e}")
        return result


def get_fleet_management_blocks():
    """
    Returns comprehensive blocks for Fleet Management workspace
    """
    return [
        # Header
        {
            "id": "header",
            "type": "header",
            "data": {
                "text": "Fleet Management",
                "col": 12
            }
        },
        
        # Quick Stats Cards
        {
            "id": "quick_stats",
            "type": "number_card",
            "data": {
                "number_card_name": "Fleet Overview",
                "col": 12,
                "cards": [
                    {
                        "name": "Total Vehicles",
                        "label": "Total Vehicles",
                        "function": "Count",
                        "aggregate_function_based_on": "Fleet Vehicle",
                        "filters": [["Fleet Vehicle", "status", "=", "Active"]],
                        "color": "Blue"
                    },
                    {
                        "name": "Active Drivers",
                        "label": "Active Drivers",
                        "function": "Count",
                        "aggregate_function_based_on": "Fleet Driver",
                        "filters": [["Fleet Driver", "status", "=", "Active"]],
                        "color": "Green"
                    },
                    {
                        "name": "Monthly Fuel Cost",
                        "label": "Monthly Fuel Cost",
                        "function": "Sum",
                        "aggregate_function_based_on": "Fuel Entry",
                        "based_on": "total_amount",
                        "filters": [["Fuel Entry", "date", "Timespan", "this month"]],
                        "color": "Orange"
                    },
                    {
                        "name": "Pending Trips",
                        "label": "Pending Trips",
                        "function": "Count",
                        "aggregate_function_based_on": "Trip",
                        "filters": [["Trip", "status", "=", "Pending"]],
                        "color": "Red"
                    }
                ]
            }
        },

        # Vehicle Management Section
        {
            "id": "vehicle_section",
            "type": "header",
            "data": {
                "text": "Vehicle Management",
                "col": 12
            }
        },
        {
            "id": "vehicle_shortcuts",
            "type": "shortcut",
            "data": {
                "shortcut_name": "Vehicle Management",
                "col": 6,
                "shortcuts": [
                    {
                        "label": "Vehicles",
                        "name": "Fleet Vehicle",
                        "type": "DocType",
                        "icon": "truck",
                        "color": "blue"
                    },
                    {
                        "label": "Vehicle Assignment",
                        "name": "Driver Vehicle Assignment",
                        "type": "DocType",
                        "icon": "user-check",
                        "color": "green"
                    },
                    {
                        "label": "Vehicle Ownership",
                        "name": "Vehicle Ownership",
                        "type": "DocType",
                        "icon": "file-text",
                        "color": "purple"
                    }
                ]
            }
        },
        {
            "id": "vehicle_chart",
            "type": "chart",
            "data": {
                "chart_name": "Vehicle Status Distribution",
                "col": 6,
                "chart_type": "Donut",
                "filters": [],
                "based_on": "status",
                "document_type": "Fleet Vehicle",
                "group_by_type": "Count",
                "time_interval": "Yearly",
                "timespan": "Last Year",
                "color": "Blue"
            }
        },

        # Driver Management Section
        {
            "id": "driver_section",
            "type": "header",
            "data": {
                "text": "Driver Management",
                "col": 12
            }
        },
        {
            "id": "driver_shortcuts",
            "type": "shortcut",
            "data": {
                "shortcut_name": "Driver Management",
                "col": 6,
                "shortcuts": [
                    {
                        "label": "Drivers",
                        "name": "Fleet Driver",
                        "type": "DocType",
                        "icon": "user",
                        "color": "blue"
                    },
                    {
                        "label": "Shifts",
                        "name": "Fleet Shift",
                        "type": "DocType",
                        "icon": "clock",
                        "color": "orange"
                    },
                    {
                        "label": "Attendance Log",
                        "name": "Fleet Access Log",
                        "type": "DocType",
                        "icon": "log-in",
                        "color": "green"
                    }
                ]
            }
        },
        {
            "id": "driver_performance_chart",
            "type": "chart",
            "data": {
                "chart_name": "Driver Performance",
                "col": 6,
                "chart_type": "Bar",
                "filters": [],
                "based_on": "creation",
                "document_type": "Trip",
                "group_by_type": "Count",
                "time_interval": "Monthly",
                "timespan": "Last 6 months",
                "color": "Green"
            }
        },

        # Operations Section
        {
            "id": "operations_section",
            "type": "header",
            "data": {
                "text": "Operations",
                "col": 12
            }
        },
        {
            "id": "operations_shortcuts",
            "type": "shortcut",
            "data": {
                "shortcut_name": "Operations",
                "col": 6,
                "shortcuts": [
                    {
                        "label": "Trips",
                        "name": "Trip",
                        "type": "DocType",
                        "icon": "map-pin",
                        "color": "blue"
                    },
                    {
                        "label": "Fuel Entry",
                        "name": "Fuel Entry",
                        "type": "DocType",
                        "icon": "zap",
                        "color": "orange"
                    },
                    {
                        "label": "Projects",
                        "name": "Fleet Project",
                        "type": "DocType",
                        "icon": "briefcase",
                        "color": "purple"
                    },
                    {
                        "label": "Branches",
                        "name": "Fleet Branch",
                        "type": "DocType",
                        "icon": "home",
                        "color": "green"
                    }
                ]
            }
        },
        {
            "id": "fuel_trend_chart",
            "type": "chart",
            "data": {
                "chart_name": "Fuel Consumption Trend",
                "col": 6,
                "chart_type": "Line",
                "filters": [],
                "based_on": "date",
                "document_type": "Fuel Entry",
                "group_by_type": "Sum",
                "group_by_based_on": "fuel_quantity",
                "time_interval": "Monthly",
                "timespan": "Last Year",
                "color": "Orange"
            }
        },

        # Reports Section
        {
            "id": "reports_section",
            "type": "header",
            "data": {
                "text": "Reports",
                "col": 12
            }
        },
        {
            "id": "reports_shortcuts",
            "type": "shortcut",
            "data": {
                "shortcut_name": "Reports",
                "col": 12,
                "shortcuts": [
                    {
                        "label": "Driver Status Report",
                        "name": "Driver Status Report",
                        "type": "Report",
                        "icon": "users",
                        "color": "blue"
                    },
                    {
                        "label": "Vehicle Status Report",
                        "name": "Vehicle Status Report",
                        "type": "Report",
                        "icon": "truck",
                        "color": "green"
                    },
                    {
                        "label": "Fuel Expenses Report",
                        "name": "Fuel Expense Report",
                        "type": "Report",
                        "icon": "dollar-sign",
                        "color": "orange"
                    },
                    {
                        "label": "Vehicle Usage Report",
                        "name": "Vehicle Utilization Report",
                        "type": "Report",
                        "icon": "bar-chart",
                        "color": "purple"
                    },
                    {
                        "label": "Monthly Costs Report",
                        "name": "Monthly Fleet Cost Report",
                        "type": "Report",
                        "icon": "calendar",
                        "color": "red"
                    }
                ]
            }
        },

        # Configuration Section
        {
            "id": "config_section",
            "type": "header",
            "data": {
                "text": "Settings",
                "col": 12
            }
        },
        {
            "id": "config_shortcuts",
            "type": "shortcut",
            "data": {
                "shortcut_name": "Configuration",
                "col": 12,
                "shortcuts": [
                    {
                        "label": "Cities",
                        "name": "Fleet City",
                        "type": "DocType",
                        "icon": "map",
                        "color": "blue"
                    },
                    {
                        "label": "Suppliers",
                        "name": "Supplier Master",
                        "type": "DocType",
                        "icon": "users",
                        "color": "green"
                    },
                    {
                        "label": "Supplier Contracts",
                        "name": "Supplier Contract",
                        "type": "DocType",
                        "icon": "file-text",
                        "color": "orange"
                    },
                    {
                        "label": "Cost Calculation Engine",
                        "name": "Cost Calculation Engine",
                        "type": "DocType",
                        "icon": "calculator",
                        "color": "purple"
                    }
                ]
            }
        }
    ]