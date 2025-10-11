# Copyright (c) 2025, AFMCOltd (afm@afmcoltd.com)
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, date_diff, add_days
from datetime import datetime, timedelta

def execute(filters=None):
    """Execute the Vehicle Utilization Report"""
    if not filters:
        filters = {}
    
    validate_filters(filters)
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data, filters)
    summary = get_summary_data(data, filters)
    
    return columns, data, None, chart, summary

def validate_filters(filters):
    """Validate report filters"""
    if not filters.get("from_date") or not filters.get("to_date"):
        frappe.throw(_("From Date and To Date are required"))
    
    if getdate(filters.get("from_date")) > getdate(filters.get("to_date")):
        frappe.throw(_("From Date cannot be greater than To Date"))

def get_columns():
    """Define report columns"""
    return [
        {
            "label": _("Vehicle"),
            "fieldname": "vehicle",
            "fieldtype": "Link",
            "options": "Fleet Vehicle",
            "width": 120
        },
        {
            "label": _("Model"),
            "fieldname": "vehicle_model",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Current Driver"),
            "fieldname": "driver",
            "fieldtype": "Link",
            "options": "Fleet Driver",
            "width": 120
        },
        {
            "label": _("Total Shifts"),
            "fieldname": "total_shifts",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "label": _("Active Days"),
            "fieldname": "active_days",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "label": _("Idle Days"),
            "fieldname": "idle_days",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "label": _("Distance (KM)"),
            "fieldname": "total_distance",
            "fieldtype": "Float",
            "width": 120,
            "precision": 2
        },
        {
            "label": _("Total Hours"),
            "fieldname": "total_hours",
            "fieldtype": "Float",
            "width": 100,
            "precision": 2
        },
        {
            "label": _("Utilization %"),
            "fieldname": "utilization_rate",
            "fieldtype": "Percent",
            "width": 120
        },
        {
            "label": _("Avg KM/Day"),
            "fieldname": "avg_distance_per_day",
            "fieldtype": "Float",
            "width": 120,
            "precision": 2
        },
        {
            "label": _("KM/Liter"),
            "fieldname": "fuel_efficiency",
            "fieldtype": "Float",
            "width": 100,
            "precision": 2
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 100
        }
    ]

def get_data(filters):
    """Get report data based on filters"""
    vehicles = get_vehicles(filters)
    
    if not vehicles:
        return []
    
    data = []
    total_days = date_diff(filters.get("to_date"), filters.get("from_date")) + 1
    
    for vehicle in vehicles:
        row = get_vehicle_utilization_data(vehicle, filters, total_days)
        if row:
            data.append(row)
    
    return data

def get_vehicles(filters):
    """Get vehicles based on filters"""
    conditions = []
    values = []
    
    if filters.get("vehicle"):
        conditions.append("name = %s")
        values.append(filters.get("vehicle"))
    
    if filters.get("branch"):
        conditions.append("branch = %s")
        values.append(filters.get("branch"))
    
    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)
    
    query = f"""
        SELECT name, vehicle_model, license_plate, branch, status
        FROM `tabFleet Vehicle`
        {where_clause}
        ORDER BY name
    """
    
    return frappe.db.sql(query, values, as_dict=True)

def get_vehicle_utilization_data(vehicle, filters, total_days):
    """Get utilization data for a specific vehicle"""
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    
    # Get current driver
    current_driver = get_current_driver(vehicle.name, to_date)
    
    # Get shift data
    shift_data = get_shift_data(vehicle.name, from_date, to_date)
    
    # Get distance data
    distance_data = get_distance_data(vehicle.name, from_date, to_date)
    
    # Get fuel efficiency
    fuel_efficiency = get_fuel_efficiency(vehicle.name, from_date, to_date)
    
    # Calculate utilization metrics
    total_shifts = shift_data.get("total_shifts", 0)
    active_days = shift_data.get("active_days", 0)
    idle_days = total_days - active_days
    total_hours = shift_data.get("total_hours", 0)
    total_distance = distance_data.get("total_distance", 0)
    
    # Calculate utilization rate (active days / total days)
    utilization_rate = (active_days / total_days * 100) if total_days > 0 else 0
    
    # Calculate average distance per day
    avg_distance_per_day = (total_distance / active_days) if active_days > 0 else 0
    
    # Determine status based on utilization threshold
    threshold = flt(filters.get("utilization_threshold", 70))
    status = get_utilization_status(utilization_rate, threshold)
    
    return {
        "vehicle": vehicle.name,
        "vehicle_model": vehicle.vehicle_model,
        "driver": current_driver,
        "total_shifts": total_shifts,
        "active_days": active_days,
        "idle_days": idle_days,
        "total_distance": total_distance,
        "total_hours": total_hours,
        "utilization_rate": utilization_rate,
        "avg_distance_per_day": avg_distance_per_day,
        "fuel_efficiency": fuel_efficiency,
        "status": status
    }

def get_current_driver(vehicle, date):
    """Get current driver for vehicle"""
    result = frappe.db.sql("""
        SELECT driver
        FROM `tabDriver Vehicle Assignment`
        WHERE vehicle = %s 
        AND assignment_date <= %s
        AND (end_date IS NULL OR end_date >= %s)
        AND docstatus = 1
        ORDER BY assignment_date DESC
        LIMIT 1
    """, (vehicle, date, date), as_dict=True)
    
    return result[0].driver if result else None

def get_shift_data(vehicle, from_date, to_date):
    """Get shift data for vehicle in date range"""
    result = frappe.db.sql("""
        SELECT 
            COUNT(*) as total_shifts,
            COUNT(DISTINCT DATE(shift_date)) as active_days,
            SUM(TIMESTAMPDIFF(HOUR, shift_start_time, shift_end_time)) as total_hours
        FROM `tabFleet Shift`
        WHERE vehicle = %s
        AND shift_date BETWEEN %s AND %s
        AND docstatus = 1
    """, (vehicle, from_date, to_date), as_dict=True)
    
    return result[0] if result else {}

def get_distance_data(vehicle, from_date, to_date):
    """Get distance data for vehicle in date range"""
    # Get distance from fuel entries (odometer readings)
    readings = frappe.db.sql("""
        SELECT odometer_reading, fuel_date
        FROM `tabFuel Entry`
        WHERE vehicle = %s
        AND fuel_date BETWEEN %s AND %s
        AND docstatus = 1
        ORDER BY fuel_date
    """, (vehicle, from_date, to_date), as_dict=True)
    
    total_distance = 0
    if len(readings) >= 2:
        # Calculate distance as difference between last and first reading
        total_distance = max(0, flt(readings[-1].odometer_reading) - flt(readings[0].odometer_reading))
    
    return {"total_distance": total_distance}

def get_fuel_efficiency(vehicle, from_date, to_date):
    """Calculate fuel efficiency for vehicle in date range"""
    # Get total fuel consumed and distance traveled
    fuel_data = frappe.db.sql("""
        SELECT 
            SUM(quantity_liters) as total_fuel,
            MAX(odometer_reading) - MIN(odometer_reading) as distance_traveled
        FROM `tabFuel Entry`
        WHERE vehicle = %s
        AND fuel_date BETWEEN %s AND %s
        AND docstatus = 1
        HAVING COUNT(*) >= 2
    """, (vehicle, from_date, to_date), as_dict=True)
    
    if fuel_data and fuel_data[0].total_fuel and fuel_data[0].distance_traveled:
        return flt(fuel_data[0].distance_traveled) / flt(fuel_data[0].total_fuel)
    
    return 0

def get_utilization_status(utilization_rate, threshold):
    """Determine utilization status based on rate and threshold"""
    if utilization_rate >= threshold:
        return "Optimal"
    elif utilization_rate >= (threshold * 0.7):
        return "Good"
    elif utilization_rate >= (threshold * 0.5):
        return "Fair"
    else:
        return "Poor"

def get_chart_data(data, filters):
    """Generate chart data for the report"""
    if not data:
        return None
    
    # Utilization rate chart
    labels = []
    utilization_rates = []
    colors = []
    
    threshold = flt(filters.get("utilization_threshold", 70))
    
    for row in data:
        labels.append(row.get("vehicle", ""))
        rate = row.get("utilization_rate", 0)
        utilization_rates.append(rate)
        
        # Color coding based on utilization
        if rate >= threshold:
            colors.append("#28a745")  # Green - Optimal
        elif rate >= (threshold * 0.7):
            colors.append("#ffc107")  # Yellow - Good
        elif rate >= (threshold * 0.5):
            colors.append("#fd7e14")  # Orange - Fair
        else:
            colors.append("#dc3545")  # Red - Poor
    
    chart = {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": _("Utilization Rate %"),
                    "values": utilization_rates
                }
            ]
        },
        "type": "bar",
        "height": 300,
        "colors": colors,
        "axisOptions": {
            "xAxisMode": "tick",
            "yAxisMode": "tick"
        },
        "barOptions": {
            "spaceRatio": 0.5
        }
    }
    
    return chart

def get_summary_data(data, filters):
    """Generate summary statistics"""
    if not data:
        return []
    
    total_vehicles = len(data)
    total_shifts = sum(row.get("total_shifts", 0) for row in data)
    total_distance = sum(row.get("total_distance", 0) for row in data)
    avg_utilization = sum(row.get("utilization_rate", 0) for row in data) / total_vehicles if total_vehicles > 0 else 0
    
    # Count vehicles by status
    status_counts = {}
    for row in data:
        status = row.get("status", "Unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    summary = [
        {
            "label": _("Total Vehicles"),
            "value": total_vehicles,
            "indicator": "Blue"
        },
        {
            "label": _("Total Shifts"),
            "value": total_shifts,
            "indicator": "Green"
        },
        {
            "label": _("Total Distance (KM)"),
            "value": f"{total_distance:,.2f}",
            "indicator": "Orange"
        },
        {
            "label": _("Average Utilization"),
            "value": f"{avg_utilization:.1f}%",
            "indicator": "Purple"
        }
    ]
    
    # Add status breakdown
    for status, count in status_counts.items():
        color = {
            "Optimal": "Green",
            "Good": "Yellow", 
            "Fair": "Orange",
            "Poor": "Red"
        }.get(status, "Gray")
        
        summary.append({
            "label": f"{status} Vehicles",
            "value": count,
            "indicator": color
        })
    
    return summary