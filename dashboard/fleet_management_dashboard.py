# Copyright (c) 2025, AFMCOltd (afm@afmcoltd.com)
# For license information, please see license.txt

import frappe
from frappe.utils import flt, getdate, add_days, date_diff, now_datetime, cint
from datetime import datetime, timedelta
import json

def get_dashboard_data(filters=None):
    """Get comprehensive dashboard data for Fleet Management"""
    if not filters:
        filters = {}
    
    data = {
        "kpis": get_fleet_kpis(filters),
        "charts": get_chart_data(filters),
        "summary": get_fleet_summary(filters),
        "alerts": get_fleet_alerts(filters),
        "recent_activities": get_recent_activities(filters)
    }
    
    return data

def get_fleet_kpis(filters=None):
    """Calculate key performance indicators for fleet management"""
    if not filters:
        filters = {}
    
    # Date range for calculations
    from_date = filters.get('from_date', add_days(getdate(), -30))
    to_date = filters.get('to_date', getdate())
    
    kpis = {}
    
    # Vehicle KPIs
    kpis['total_vehicles'] = get_total_vehicles()
    kpis['active_vehicles'] = get_active_vehicles()
    kpis['vehicle_utilization'] = get_vehicle_utilization_rate(from_date, to_date)
    kpis['vehicles_in_maintenance'] = get_vehicles_in_maintenance()
    
    # Driver KPIs
    kpis['total_drivers'] = get_total_drivers()
    kpis['active_drivers'] = get_active_drivers()
    kpis['driver_utilization'] = get_driver_utilization_rate(from_date, to_date)
    kpis['drivers_on_leave'] = get_drivers_on_leave()
    
    # Cost KPIs
    kpis['total_fleet_cost'] = get_total_fleet_cost(from_date, to_date)
    kpis['fuel_cost'] = get_fuel_cost(from_date, to_date)
    kpis['maintenance_cost'] = get_maintenance_cost(from_date, to_date)
    kpis['cost_per_km'] = get_average_cost_per_km(from_date, to_date)
    
    # Operational KPIs
    kpis['total_shifts'] = get_total_shifts(from_date, to_date)
    kpis['completed_shifts'] = get_completed_shifts(from_date, to_date)
    kpis['cancelled_shifts'] = get_cancelled_shifts(from_date, to_date)
    kpis['shift_completion_rate'] = calculate_completion_rate(kpis['completed_shifts'], kpis['total_shifts'])
    
    # Distance and Fuel KPIs
    kpis['total_distance'] = get_total_distance(from_date, to_date)
    kpis['total_fuel_consumed'] = get_total_fuel_consumed(from_date, to_date)
    kpis['average_fuel_efficiency'] = calculate_fuel_efficiency(kpis['total_distance'], kpis['total_fuel_consumed'])
    
    # Performance KPIs
    kpis['on_time_performance'] = get_on_time_performance(from_date, to_date)
    kpis['safety_incidents'] = get_safety_incidents(from_date, to_date)
    kpis['customer_satisfaction'] = get_customer_satisfaction_score(from_date, to_date)
    
    return kpis

def get_chart_data(filters=None):
    """Get data for dashboard charts"""
    if not filters:
        filters = {}
    
    charts = {}
    
    # Monthly cost trend
    charts['monthly_costs'] = get_monthly_cost_trend()
    
    # Vehicle utilization chart
    charts['vehicle_utilization'] = get_vehicle_utilization_chart()
    
    # Fuel consumption trend
    charts['fuel_trend'] = get_fuel_consumption_trend()
    
    # Driver performance chart
    charts['driver_performance'] = get_driver_performance_chart()
    
    # Cost breakdown pie chart
    charts['cost_breakdown'] = get_cost_breakdown_chart()
    
    # Vehicle status distribution
    charts['vehicle_status'] = get_vehicle_status_distribution()
    
    # Branch performance comparison
    charts['branch_performance'] = get_branch_performance_chart()
    
    return charts

def get_fleet_summary(filters=None):
    """Get fleet summary statistics"""
    if not filters:
        filters = {}
    
    summary = {
        "fleet_size": get_total_vehicles(),
        "active_fleet_percentage": calculate_percentage(get_active_vehicles(), get_total_vehicles()),
        "average_vehicle_age": get_average_vehicle_age(),
        "total_mileage": get_total_fleet_mileage(),
        "maintenance_due": get_vehicles_maintenance_due(),
        "insurance_expiring": get_vehicles_insurance_expiring(),
        "registration_expiring": get_vehicles_registration_expiring()
    }
    
    return summary

def get_fleet_alerts(filters=None):
    """Get fleet management alerts and notifications"""
    alerts = []
    
    # Maintenance due alerts
    maintenance_due = frappe.db.sql("""
        SELECT vehicle_number, next_maintenance_date
        FROM `tabFleet Vehicle`
        WHERE next_maintenance_date <= %s
        AND status = 'Active'
        ORDER BY next_maintenance_date
    """, (add_days(getdate(), 7),))
    
    for vehicle, due_date in maintenance_due:
        alerts.append({
            "type": "warning",
            "title": "Maintenance Due",
            "message": f"Vehicle {vehicle} maintenance due on {due_date}",
            "priority": "high"
        })
    
    # Insurance expiring alerts
    insurance_expiring = frappe.db.sql("""
        SELECT vo.vehicle, vo.insurance_expiry_date
        FROM `tabVehicle Ownership` vo
        WHERE vo.insurance_expiry_date <= %s
        AND vo.insurance_expiry_date >= %s
        ORDER BY vo.insurance_expiry_date
    """, (add_days(getdate(), 30), getdate()))
    
    for vehicle, expiry_date in insurance_expiring:
        alerts.append({
            "type": "danger",
            "title": "Insurance Expiring",
            "message": f"Vehicle {vehicle} insurance expires on {expiry_date}",
            "priority": "high"
        })
    
    # High fuel consumption alerts
    high_fuel_vehicles = frappe.db.sql("""
        SELECT vehicle, AVG(quantity_liters/distance_traveled) as avg_consumption
        FROM `tabFuel Entry`
        WHERE fuel_date >= %s
        AND distance_traveled > 0
        GROUP BY vehicle
        HAVING avg_consumption > 0.15
        ORDER BY avg_consumption DESC
        LIMIT 5
    """, (add_days(getdate(), -30),))
    
    for vehicle, consumption in high_fuel_vehicles:
        alerts.append({
            "type": "info",
            "title": "High Fuel Consumption",
            "message": f"Vehicle {vehicle} has high fuel consumption: {consumption:.2f} L/km",
            "priority": "medium"
        })
    
    return alerts

def get_recent_activities(filters=None):
    """Get recent fleet management activities"""
    activities = []
    
    # Recent fuel entries
    recent_fuel = frappe.db.sql("""
        SELECT vehicle, fuel_date, total_amount, fuel_station
        FROM `tabFuel Entry`
        WHERE fuel_date >= %s
        ORDER BY fuel_date DESC
        LIMIT 10
    """, (add_days(getdate(), -7),))
    
    for vehicle, date, amount, station in recent_fuel:
        activities.append({
            "type": "fuel",
            "title": f"Fuel Entry - {vehicle}",
            "description": f"Fueled at {station} for {amount}",
            "date": date,
            "icon": "fa fa-gas-pump"
        })
    
    # Recent shifts
    recent_shifts = frappe.db.sql("""
        SELECT vehicle, driver, shift_date, status
        FROM `tabFleet Shift`
        WHERE shift_date >= %s
        ORDER BY shift_date DESC
        LIMIT 10
    """, (add_days(getdate(), -3),))
    
    for vehicle, driver, date, status in recent_shifts:
        activities.append({
            "type": "shift",
            "title": f"Shift - {vehicle}",
            "description": f"Driver: {driver}, Status: {status}",
            "date": date,
            "icon": "fa fa-calendar"
        })
    
    # Sort activities by date
    activities.sort(key=lambda x: x['date'], reverse=True)
    
    return activities[:20]  # Return latest 20 activities

# Helper functions for KPI calculations
def get_total_vehicles():
    """Get total number of vehicles"""
    return frappe.db.count("Fleet Vehicle")

def get_active_vehicles():
    """Get number of active vehicles"""
    return frappe.db.count("Fleet Vehicle", {"status": "Active"})

def get_vehicle_utilization_rate(from_date, to_date):
    """Calculate average vehicle utilization rate"""
    result = frappe.db.sql("""
        SELECT AVG(utilization_rate)
        FROM `tabFleet Vehicle`
        WHERE status = 'Active'
    """)
    
    return flt(result[0][0]) if result and result[0][0] else 0

def get_vehicles_in_maintenance():
    """Get number of vehicles currently in maintenance"""
    return frappe.db.count("Fleet Vehicle", {"status": "Maintenance"})

def get_total_drivers():
    """Get total number of drivers"""
    return frappe.db.count("Fleet Driver")

def get_active_drivers():
    """Get number of active drivers"""
    return frappe.db.count("Fleet Driver", {"status": "Active"})

def get_driver_utilization_rate(from_date, to_date):
    """Calculate driver utilization rate"""
    total_drivers = get_active_drivers()
    if total_drivers == 0:
        return 0
    
    active_drivers = frappe.db.sql("""
        SELECT COUNT(DISTINCT driver)
        FROM `tabFleet Shift`
        WHERE shift_date BETWEEN %s AND %s
        AND status IN ('Active', 'Completed')
    """, (from_date, to_date))
    
    active_count = active_drivers[0][0] if active_drivers else 0
    return (active_count / total_drivers) * 100

def get_drivers_on_leave():
    """Get number of drivers on leave"""
    return frappe.db.count("Fleet Driver", {"status": "On Leave"})

def get_total_fleet_cost(from_date, to_date):
    """Get total fleet cost for date range"""
    result = frappe.db.sql("""
        SELECT SUM(total_cost)
        FROM `tabCost Calculation Engine`
        WHERE creation_date BETWEEN %s AND %s
        AND status = 'Completed'
    """, (from_date, to_date))
    
    return flt(result[0][0]) if result and result[0][0] else 0

def get_fuel_cost(from_date, to_date):
    """Get total fuel cost for date range"""
    result = frappe.db.sql("""
        SELECT SUM(total_amount)
        FROM `tabFuel Entry`
        WHERE fuel_date BETWEEN %s AND %s
        AND docstatus = 1
    """, (from_date, to_date))
    
    return flt(result[0][0]) if result and result[0][0] else 0

def get_maintenance_cost(from_date, to_date):
    """Get total maintenance cost for date range"""
    result = frappe.db.sql("""
        SELECT SUM(maintenance_cost)
        FROM `tabCost Calculation Engine`
        WHERE creation_date BETWEEN %s AND %s
        AND status = 'Completed'
    """, (from_date, to_date))
    
    return flt(result[0][0]) if result and result[0][0] else 0

def get_average_cost_per_km(from_date, to_date):
    """Calculate average cost per kilometer"""
    total_cost = get_total_fleet_cost(from_date, to_date)
    total_distance = get_total_distance(from_date, to_date)
    
    if total_distance > 0:
        return total_cost / total_distance
    return 0

def get_total_shifts(from_date, to_date):
    """Get total number of shifts"""
    return frappe.db.count("Fleet Shift", {
        "shift_date": ["between", [from_date, to_date]]
    })

def get_completed_shifts(from_date, to_date):
    """Get number of completed shifts"""
    return frappe.db.count("Fleet Shift", {
        "shift_date": ["between", [from_date, to_date]],
        "status": "Completed"
    })

def get_cancelled_shifts(from_date, to_date):
    """Get number of cancelled shifts"""
    return frappe.db.count("Fleet Shift", {
        "shift_date": ["between", [from_date, to_date]],
        "status": "Cancelled"
    })

def get_total_distance(from_date, to_date):
    """Get total distance traveled"""
    result = frappe.db.sql("""
        SELECT SUM(distance_traveled)
        FROM `tabFuel Entry`
        WHERE fuel_date BETWEEN %s AND %s
        AND distance_traveled > 0
    """, (from_date, to_date))
    
    return flt(result[0][0]) if result and result[0][0] else 0

def get_total_fuel_consumed(from_date, to_date):
    """Get total fuel consumed"""
    result = frappe.db.sql("""
        SELECT SUM(quantity_liters)
        FROM `tabFuel Entry`
        WHERE fuel_date BETWEEN %s AND %s
    """, (from_date, to_date))
    
    return flt(result[0][0]) if result and result[0][0] else 0

def get_on_time_performance(from_date, to_date):
    """Calculate on-time performance percentage"""
    total_shifts = get_total_shifts(from_date, to_date)
    if total_shifts == 0:
        return 0
    
    on_time_shifts = frappe.db.count("Fleet Shift", {
        "shift_date": ["between", [from_date, to_date]],
        "status": "Completed",
        "delay_minutes": ["<=", 15]  # Consider on-time if delay <= 15 minutes
    })
    
    return (on_time_shifts / total_shifts) * 100

def get_safety_incidents(from_date, to_date):
    """Get number of safety incidents"""
    # Placeholder - would integrate with incident management system
    return 0

def get_customer_satisfaction_score(from_date, to_date):
    """Get customer satisfaction score"""
    # Placeholder - would integrate with customer feedback system
    return 85.5

# Chart data functions
def get_monthly_cost_trend():
    """Get monthly cost trend data"""
    result = frappe.db.sql("""
        SELECT 
            DATE_FORMAT(creation_date, '%Y-%m') as month,
            SUM(total_cost) as total_cost
        FROM `tabCost Calculation Engine`
        WHERE creation_date >= %s
        AND status = 'Completed'
        GROUP BY DATE_FORMAT(creation_date, '%Y-%m')
        ORDER BY month
    """, (add_days(getdate(), -365),))
    
    return [{"month": month, "cost": flt(cost)} for month, cost in result]

def get_vehicle_utilization_chart():
    """Get vehicle utilization chart data"""
    result = frappe.db.sql("""
        SELECT vehicle_number, utilization_rate
        FROM `tabFleet Vehicle`
        WHERE status = 'Active'
        ORDER BY utilization_rate DESC
        LIMIT 10
    """)
    
    return [{"vehicle": vehicle, "utilization": flt(rate)} for vehicle, rate in result]

def get_fuel_consumption_trend():
    """Get fuel consumption trend data"""
    result = frappe.db.sql("""
        SELECT 
            DATE_FORMAT(fuel_date, '%Y-%m') as month,
            SUM(quantity_liters) as fuel_consumed
        FROM `tabFuel Entry`
        WHERE fuel_date >= %s
        GROUP BY DATE_FORMAT(fuel_date, '%Y-%m')
        ORDER BY month
    """, (add_days(getdate(), -365),))
    
    return [{"month": month, "fuel": flt(fuel)} for month, fuel in result]

def get_driver_performance_chart():
    """Get driver performance chart data"""
    result = frappe.db.sql("""
        SELECT 
            driver,
            COUNT(*) as total_shifts,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_shifts
        FROM `tabFleet Shift`
        WHERE shift_date >= %s
        GROUP BY driver
        ORDER BY completed_shifts DESC
        LIMIT 10
    """, (add_days(getdate(), -30),))
    
    return [{
        "driver": driver,
        "total_shifts": total,
        "completed_shifts": completed,
        "completion_rate": (completed / total * 100) if total > 0 else 0
    } for driver, total, completed in result]

def get_cost_breakdown_chart():
    """Get cost breakdown chart data"""
    result = frappe.db.sql("""
        SELECT 
            SUM(fuel_cost) as fuel,
            SUM(maintenance_cost) as maintenance,
            SUM(insurance_cost) as insurance,
            SUM(driver_salary) as salary,
            SUM(depreciation_cost) as depreciation,
            SUM(other_costs) as other
        FROM `tabCost Calculation Engine`
        WHERE creation_date >= %s
        AND status = 'Completed'
    """, (add_days(getdate(), -30),))
    
    if result and result[0]:
        fuel, maintenance, insurance, salary, depreciation, other = result[0]
        return [
            {"category": "Fuel", "amount": flt(fuel)},
            {"category": "Maintenance", "amount": flt(maintenance)},
            {"category": "Insurance", "amount": flt(insurance)},
            {"category": "Driver Salary", "amount": flt(salary)},
            {"category": "Depreciation", "amount": flt(depreciation)},
            {"category": "Other", "amount": flt(other)}
        ]
    
    return []

def get_vehicle_status_distribution():
    """Get vehicle status distribution data"""
    result = frappe.db.sql("""
        SELECT status, COUNT(*) as count
        FROM `tabFleet Vehicle`
        GROUP BY status
    """)
    
    return [{"status": status, "count": count} for status, count in result]

def get_branch_performance_chart():
    """Get branch performance chart data"""
    result = frappe.db.sql("""
        SELECT 
            branch,
            SUM(total_cost) as total_cost,
            COUNT(DISTINCT vehicle) as vehicle_count
        FROM `tabCost Calculation Engine`
        WHERE creation_date >= %s
        AND status = 'Completed'
        GROUP BY branch
        ORDER BY total_cost DESC
    """, (add_days(getdate(), -30),))
    
    return [{
        "branch": branch,
        "total_cost": flt(cost),
        "vehicle_count": count,
        "cost_per_vehicle": flt(cost) / count if count > 0 else 0
    } for branch, cost, count in result]

# Utility functions
def calculate_completion_rate(completed, total):
    """Calculate completion rate percentage"""
    if total > 0:
        return (completed / total) * 100
    return 0

def calculate_fuel_efficiency(distance, fuel):
    """Calculate fuel efficiency (km per liter)"""
    if fuel > 0:
        return distance / fuel
    return 0

def calculate_percentage(part, total):
    """Calculate percentage"""
    if total > 0:
        return (part / total) * 100
    return 0

def get_average_vehicle_age():
    """Get average age of fleet vehicles"""
    result = frappe.db.sql("""
        SELECT AVG(YEAR(CURDATE()) - model_year) as avg_age
        FROM `tabFleet Vehicle`
        WHERE model_year IS NOT NULL
    """)
    
    return flt(result[0][0]) if result and result[0][0] else 0

def get_total_fleet_mileage():
    """Get total fleet mileage"""
    result = frappe.db.sql("""
        SELECT SUM(current_odometer_reading) as total_mileage
        FROM `tabFleet Vehicle`
        WHERE current_odometer_reading IS NOT NULL
    """)
    
    return flt(result[0][0]) if result and result[0][0] else 0

def get_vehicles_maintenance_due():
    """Get count of vehicles with maintenance due"""
    return frappe.db.count("Fleet Vehicle", {
        "next_maintenance_date": ["<=", add_days(getdate(), 7)],
        "status": "Active"
    })

def get_vehicles_insurance_expiring():
    """Get count of vehicles with insurance expiring soon"""
    return frappe.db.sql("""
        SELECT COUNT(*)
        FROM `tabVehicle Ownership`
        WHERE insurance_expiry_date BETWEEN %s AND %s
    """, (getdate(), add_days(getdate(), 30)))[0][0]

def get_vehicles_registration_expiring():
    """Get count of vehicles with registration expiring soon"""
    return frappe.db.sql("""
        SELECT COUNT(*)
        FROM `tabVehicle Ownership`
        WHERE registration_expiry_date BETWEEN %s AND %s
    """, (getdate(), add_days(getdate(), 30)))[0][0]