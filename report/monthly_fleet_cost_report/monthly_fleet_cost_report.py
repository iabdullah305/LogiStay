# Copyright (c) 2025, AFMCOltd (afm@afmcoltd.com)
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, add_months, get_first_day, get_last_day
from datetime import datetime
import calendar

def execute(filters=None):
    """Execute the Monthly Fleet Cost Report"""
    if not filters:
        filters = {}
    
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data, filters)
    
    return columns, data, None, chart

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
            "label": _("Driver"),
            "fieldname": "driver",
            "fieldtype": "Link",
            "options": "Fleet Driver",
            "width": 120
        },
        {
            "label": _("Fuel Cost"),
            "fieldname": "fuel_cost",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("Maintenance Cost"),
            "fieldname": "maintenance_cost",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Insurance Cost"),
            "fieldname": "insurance_cost",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Driver Salary"),
            "fieldname": "driver_salary",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Depreciation"),
            "fieldname": "depreciation_cost",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Other Costs"),
            "fieldname": "other_costs",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("Total Cost"),
            "fieldname": "total_cost",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Distance (KM)"),
            "fieldname": "distance_traveled",
            "fieldtype": "Float",
            "width": 100,
            "precision": 2
        },
        {
            "label": _("Cost per KM"),
            "fieldname": "cost_per_km",
            "fieldtype": "Currency",
            "width": 100
        }
    ]

def get_data(filters):
    """Get report data based on filters"""
    conditions = get_conditions(filters)
    
    # Get vehicle list based on filters
    vehicles = get_vehicles(filters)
    
    if not vehicles:
        return []
    
    data = []
    
    for vehicle in vehicles:
        row = get_vehicle_cost_data(vehicle, filters)
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
        SELECT name, vehicle_model, license_plate, branch
        FROM `tabFleet Vehicle`
        {where_clause}
        ORDER BY name
    """
    
    return frappe.db.sql(query, values, as_dict=True)

def get_vehicle_cost_data(vehicle, filters):
    """Get cost data for a specific vehicle"""
    month = filters.get("month")
    year = filters.get("year")
    
    if not month or not year:
        return None
    
    # Convert month name to number
    month_num = list(calendar.month_name).index(month)
    
    # Get date range for the month
    start_date = get_first_day(f"{year}-{month_num:02d}-01")
    end_date = get_last_day(f"{year}-{month_num:02d}-01")
    
    # Get current driver assignment
    driver = get_current_driver(vehicle.name, end_date)
    
    # Calculate costs
    fuel_cost = get_fuel_cost(vehicle.name, start_date, end_date)
    maintenance_cost = get_maintenance_cost(vehicle.name, start_date, end_date)
    insurance_cost = get_insurance_cost(vehicle.name, start_date, end_date)
    driver_salary = get_driver_salary(driver, start_date, end_date) if driver else 0
    depreciation_cost = get_depreciation_cost(vehicle.name, start_date, end_date)
    other_costs = get_other_costs(vehicle.name, start_date, end_date)
    distance_traveled = get_distance_traveled(vehicle.name, start_date, end_date)
    
    total_cost = fuel_cost + maintenance_cost + insurance_cost + driver_salary + depreciation_cost + other_costs
    cost_per_km = total_cost / distance_traveled if distance_traveled > 0 else 0
    
    return {
        "vehicle": vehicle.name,
        "vehicle_model": vehicle.vehicle_model,
        "driver": driver,
        "fuel_cost": fuel_cost,
        "maintenance_cost": maintenance_cost,
        "insurance_cost": insurance_cost,
        "driver_salary": driver_salary,
        "depreciation_cost": depreciation_cost,
        "other_costs": other_costs,
        "total_cost": total_cost,
        "distance_traveled": distance_traveled,
        "cost_per_km": cost_per_km
    }

def get_current_driver(vehicle, date):
    """Get current driver for vehicle"""
    driver = frappe.db.sql("""
        SELECT driver
        FROM `tabDriver Vehicle Assignment`
        WHERE vehicle = %s 
        AND assignment_date <= %s
        AND (end_date IS NULL OR end_date >= %s)
        AND docstatus = 1
        ORDER BY assignment_date DESC
        LIMIT 1
    """, (vehicle, date, date))
    
    return driver[0][0] if driver else None

def get_fuel_cost(vehicle, start_date, end_date):
    """Calculate fuel cost for vehicle in date range"""
    fuel_cost = frappe.db.sql("""
        SELECT COALESCE(SUM(total_amount), 0) as fuel_cost
        FROM `tabFuel Entry`
        WHERE vehicle = %s
        AND fuel_date BETWEEN %s AND %s
        AND docstatus = 1
    """, (vehicle, start_date, end_date))
    
    return flt(fuel_cost[0][0]) if fuel_cost else 0

def get_maintenance_cost(vehicle, start_date, end_date):
    """Calculate maintenance cost for vehicle in date range"""
    # This would typically come from a Maintenance Entry DocType
    # For now, return 0 as placeholder
    return 0

def get_insurance_cost(vehicle, start_date, end_date):
    """Calculate insurance cost for vehicle in date range"""
    # Get monthly insurance cost from vehicle ownership
    insurance_cost = frappe.db.sql("""
        SELECT COALESCE(insurance_premium_monthly, 0) as insurance_cost
        FROM `tabVehicle Ownership`
        WHERE vehicle = %s
        AND start_date <= %s
        AND (end_date IS NULL OR end_date >= %s)
        ORDER BY start_date DESC
        LIMIT 1
    """, (vehicle, end_date, start_date))
    
    return flt(insurance_cost[0][0]) if insurance_cost else 0

def get_driver_salary(driver, start_date, end_date):
    """Calculate driver salary for date range"""
    if not driver:
        return 0
    
    # Get driver salary from Fleet Driver
    salary = frappe.db.get_value("Fleet Driver", driver, "monthly_salary")
    return flt(salary) if salary else 0

def get_depreciation_cost(vehicle, start_date, end_date):
    """Calculate depreciation cost for vehicle in date range"""
    # Get monthly depreciation from vehicle ownership
    depreciation = frappe.db.sql("""
        SELECT COALESCE(monthly_depreciation, 0) as depreciation
        FROM `tabVehicle Ownership`
        WHERE vehicle = %s
        AND start_date <= %s
        AND (end_date IS NULL OR end_date >= %s)
        ORDER BY start_date DESC
        LIMIT 1
    """, (vehicle, end_date, start_date))
    
    return flt(depreciation[0][0]) if depreciation else 0

def get_other_costs(vehicle, start_date, end_date):
    """Calculate other costs for vehicle in date range"""
    # This would include registration fees, fines, etc.
    # For now, return 0 as placeholder
    return 0

def get_distance_traveled(vehicle, start_date, end_date):
    """Calculate distance traveled by vehicle in date range"""
    # Get distance from fuel entries (odometer readings)
    readings = frappe.db.sql("""
        SELECT odometer_reading
        FROM `tabFuel Entry`
        WHERE vehicle = %s
        AND fuel_date BETWEEN %s AND %s
        AND docstatus = 1
        ORDER BY fuel_date
    """, (vehicle, start_date, end_date))
    
    if len(readings) < 2:
        return 0
    
    # Calculate distance as difference between last and first reading
    distance = flt(readings[-1][0]) - flt(readings[0][0])
    return max(distance, 0)

def get_conditions(filters):
    """Build SQL conditions from filters"""
    conditions = []
    
    if filters.get("vehicle"):
        conditions.append("vehicle = %(vehicle)s")
    
    if filters.get("driver"):
        conditions.append("driver = %(driver)s")
    
    if filters.get("branch"):
        conditions.append("branch = %(branch)s")
    
    return " AND ".join(conditions)

def get_chart_data(data, filters):
    """Generate chart data for the report"""
    if not data:
        return None
    
    # Cost breakdown chart
    labels = []
    fuel_costs = []
    maintenance_costs = []
    insurance_costs = []
    driver_salaries = []
    
    for row in data:
        labels.append(row.get("vehicle", ""))
        fuel_costs.append(row.get("fuel_cost", 0))
        maintenance_costs.append(row.get("maintenance_cost", 0))
        insurance_costs.append(row.get("insurance_cost", 0))
        driver_salaries.append(row.get("driver_salary", 0))
    
    chart = {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": _("Fuel Cost"),
                    "values": fuel_costs
                },
                {
                    "name": _("Maintenance Cost"),
                    "values": maintenance_costs
                },
                {
                    "name": _("Insurance Cost"),
                    "values": insurance_costs
                },
                {
                    "name": _("Driver Salary"),
                    "values": driver_salaries
                }
            ]
        },
        "type": "bar",
        "height": 300,
        "colors": ["#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4"]
    }
    
    return chart