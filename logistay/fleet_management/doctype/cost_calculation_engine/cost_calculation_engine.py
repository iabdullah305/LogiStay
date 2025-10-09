# Copyright (c) 2025, AFMCOltd (afm@afmcoltd.com)
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, add_days, date_diff, now_datetime
from datetime import datetime
import json

class CostCalculationEngine(Document):
    def before_save(self):
        """Execute before saving the document"""
        self.set_defaults()
        self.validate_data()
        self.calculate_costs()
        self.update_audit_fields()
    
    def on_update(self):
        """Execute after updating the document"""
        if self.status == "Completed":
            self.log_calculation("Cost calculation completed successfully")
    
    def set_defaults(self):
        """Set default values"""
        if not self.creation_date:
            self.creation_date = now_datetime()
        
        if not self.created_by:
            self.created_by = frappe.session.user
        
        if not self.status:
            self.status = "Draft"
        
        if not self.priority:
            self.priority = "Medium"
        
        if not self.calculation_method:
            self.calculation_method = "Actual Cost"
        
        if not self.depreciation_method:
            self.depreciation_method = "Straight Line"
        
        if not self.fuel_price_source:
            self.fuel_price_source = "Actual Receipts"
    
    def validate_data(self):
        """Validate calculation data"""
        try:
            # Validate date ranges
            if self.calculation_period_from and self.calculation_period_to:
                if getdate(self.calculation_period_from) > getdate(self.calculation_period_to):
                    frappe.throw("Calculation Period From cannot be greater than Calculation Period To")
            
            # Validate vehicle and driver combination
            if self.vehicle and self.driver:
                self.validate_vehicle_driver_assignment()
            
            # Validate cost components
            self.validate_cost_components()
            
            self.validation_status = "Valid"
            
        except Exception as e:
            self.validation_status = "Invalid"
            self.error_log = str(e)
            self.log_calculation(f"Validation error: {str(e)}")
    
    def validate_vehicle_driver_assignment(self):
        """Validate if driver is assigned to vehicle"""
        if not self.calculation_period_to:
            check_date = getdate()
        else:
            check_date = getdate(self.calculation_period_to)
        
        assignment = frappe.db.sql("""
            SELECT name
            FROM `tabDriver Vehicle Assignment`
            WHERE vehicle = %s AND driver = %s
            AND assignment_date <= %s
            AND (end_date IS NULL OR end_date >= %s)
            AND docstatus = 1
        """, (self.vehicle, self.driver, check_date, check_date))
        
        if not assignment:
            frappe.msgprint(f"Warning: Driver {self.driver} is not assigned to vehicle {self.vehicle} for the calculation period")
    
    def validate_cost_components(self):
        """Validate cost component values"""
        cost_fields = [
            'fuel_cost', 'maintenance_cost', 'insurance_cost', 'driver_salary',
            'depreciation_cost', 'registration_cost', 'penalty_cost', 'allowance_cost',
            'overtime_cost', 'bonus_cost', 'other_costs', 'tax_amount'
        ]
        
        for field in cost_fields:
            value = getattr(self, field, 0)
            if value and flt(value) < 0:
                frappe.throw(f"{field.replace('_', ' ').title()} cannot be negative")
    
    def calculate_costs(self):
        """Main cost calculation method"""
        try:
            self.status = "Calculating"
            self.log_calculation("Starting cost calculation")
            
            # Calculate individual cost components
            if self.calculation_type in ["Vehicle Cost", "Monthly Cost", "Yearly Cost"]:
                self.calculate_vehicle_costs()
            
            if self.calculation_type in ["Driver Cost", "Monthly Cost", "Yearly Cost"]:
                self.calculate_driver_costs()
            
            if self.calculation_type == "Route Cost":
                self.calculate_route_costs()
            
            if self.calculation_type == "Project Cost":
                self.calculate_project_costs()
            
            # Calculate totals and ratios
            self.calculate_totals()
            self.calculate_efficiency_metrics()
            
            # Create cost breakdown
            self.create_cost_breakdown()
            
            self.status = "Completed"
            self.log_calculation("Cost calculation completed successfully")
            
        except Exception as e:
            self.status = "Error"
            self.error_log = str(e)
            self.log_calculation(f"Calculation error: {str(e)}")
            frappe.log_error(f"Cost Calculation Error: {str(e)}", "Cost Calculation Engine")
    
    def calculate_vehicle_costs(self):
        """Calculate vehicle-related costs"""
        if not self.vehicle:
            return
        
        period_from = self.calculation_period_from or add_days(getdate(), -30)
        period_to = self.calculation_period_to or getdate()
        
        # Fuel costs
        if not self.fuel_cost:
            self.fuel_cost = self.get_fuel_cost(self.vehicle, period_from, period_to)
        
        # Maintenance costs
        if not self.maintenance_cost:
            self.maintenance_cost = self.get_maintenance_cost(self.vehicle, period_from, period_to)
        
        # Insurance costs
        if not self.insurance_cost:
            self.insurance_cost = self.get_insurance_cost(self.vehicle, period_from, period_to)
        
        # Depreciation costs
        if not self.depreciation_cost:
            self.depreciation_cost = self.get_depreciation_cost(self.vehicle, period_from, period_to)
        
        # Registration costs
        if not self.registration_cost:
            self.registration_cost = self.get_registration_cost(self.vehicle, period_from, period_to)
        
        # Get vehicle metrics
        self.distance_traveled = self.get_distance_traveled(self.vehicle, period_from, period_to)
        self.days_active = self.get_active_days(self.vehicle, period_from, period_to)
    
    def calculate_driver_costs(self):
        """Calculate driver-related costs"""
        if not self.driver:
            return
        
        period_from = self.calculation_period_from or add_days(getdate(), -30)
        period_to = self.calculation_period_to or getdate()
        
        # Driver salary
        if not self.driver_salary:
            self.driver_salary = self.get_driver_salary(self.driver, period_from, period_to)
        
        # Allowances
        if not self.allowance_cost:
            self.allowance_cost = self.get_driver_allowances(self.driver, period_from, period_to)
        
        # Overtime
        if not self.overtime_cost:
            self.overtime_cost = self.get_overtime_cost(self.driver, period_from, period_to)
        
        # Bonuses
        if not self.bonus_cost:
            self.bonus_cost = self.get_bonus_cost(self.driver, period_from, period_to)
        
        # Penalties
        if not self.penalty_cost:
            self.penalty_cost = self.get_penalty_cost(self.driver, period_from, period_to)
        
        # Get driver metrics
        self.hours_worked = self.get_hours_worked(self.driver, period_from, period_to)
    
    def calculate_route_costs(self):
        """Calculate route-specific costs"""
        # This would be implemented based on route data
        # For now, use vehicle and driver costs
        self.calculate_vehicle_costs()
        self.calculate_driver_costs()
    
    def calculate_project_costs(self):
        """Calculate project-specific costs"""
        # This would be implemented based on project data
        # For now, use vehicle and driver costs
        self.calculate_vehicle_costs()
        self.calculate_driver_costs()
    
    def calculate_totals(self):
        """Calculate total costs and ratios"""
        cost_components = [
            self.fuel_cost or 0,
            self.maintenance_cost or 0,
            self.insurance_cost or 0,
            self.driver_salary or 0,
            self.depreciation_cost or 0,
            self.registration_cost or 0,
            self.penalty_cost or 0,
            self.allowance_cost or 0,
            self.overtime_cost or 0,
            self.bonus_cost or 0,
            self.other_costs or 0,
            self.tax_amount or 0
        ]
        
        self.total_cost = sum(flt(cost) for cost in cost_components)
        
        # Calculate ratios
        if self.distance_traveled and flt(self.distance_traveled) > 0:
            self.cost_per_km = self.total_cost / flt(self.distance_traveled)
        
        if self.hours_worked and flt(self.hours_worked) > 0:
            self.cost_per_hour = self.total_cost / flt(self.hours_worked)
        
        if self.days_active and flt(self.days_active) > 0:
            self.cost_per_day = self.total_cost / flt(self.days_active)
    
    def calculate_efficiency_metrics(self):
        """Calculate efficiency metrics"""
        if self.vehicle and self.distance_traveled:
            period_from = self.calculation_period_from or add_days(getdate(), -30)
            period_to = self.calculation_period_to or getdate()
            
            # Calculate fuel efficiency
            total_fuel = self.get_total_fuel_consumed(self.vehicle, period_from, period_to)
            if total_fuel and flt(total_fuel) > 0:
                self.fuel_efficiency = flt(self.distance_traveled) / flt(total_fuel)
    
    def create_cost_breakdown(self):
        """Create detailed cost breakdown table"""
        self.cost_breakdown_table = []
        
        cost_items = [
            ("Fuel Cost", self.fuel_cost or 0),
            ("Maintenance Cost", self.maintenance_cost or 0),
            ("Insurance Cost", self.insurance_cost or 0),
            ("Driver Salary", self.driver_salary or 0),
            ("Depreciation Cost", self.depreciation_cost or 0),
            ("Registration Cost", self.registration_cost or 0),
            ("Penalty Cost", self.penalty_cost or 0),
            ("Allowance Cost", self.allowance_cost or 0),
            ("Overtime Cost", self.overtime_cost or 0),
            ("Bonus Cost", self.bonus_cost or 0),
            ("Other Costs", self.other_costs or 0),
            ("Tax Amount", self.tax_amount or 0)
        ]
        
        for item_name, amount in cost_items:
            if flt(amount) > 0:
                percentage = (flt(amount) / self.total_cost * 100) if self.total_cost > 0 else 0
                
                self.append("cost_breakdown_table", {
                    "cost_item": item_name,
                    "amount": amount,
                    "percentage": percentage,
                    "description": f"{item_name} for the calculation period"
                })
    
    def update_audit_fields(self):
        """Update audit trail fields"""
        self.last_modified = now_datetime()
        self.modified_by = frappe.session.user
    
    def log_calculation(self, message):
        """Log calculation steps"""
        timestamp = now_datetime().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        if self.calculation_log:
            self.calculation_log += log_entry
        else:
            self.calculation_log = log_entry
    
    # Helper methods for cost calculations
    def get_fuel_cost(self, vehicle, from_date, to_date):
        """Get fuel cost for vehicle in date range"""
        result = frappe.db.sql("""
            SELECT COALESCE(SUM(total_amount), 0) as fuel_cost
            FROM `tabFuel Entry`
            WHERE vehicle = %s
            AND fuel_date BETWEEN %s AND %s
            AND docstatus = 1
        """, (vehicle, from_date, to_date))
        
        return flt(result[0][0]) if result else 0
    
    def get_maintenance_cost(self, vehicle, from_date, to_date):
        """Get maintenance cost for vehicle in date range"""
        # Placeholder - would integrate with maintenance module
        return 0
    
    def get_insurance_cost(self, vehicle, from_date, to_date):
        """Get insurance cost for vehicle in date range"""
        # Get monthly insurance from vehicle ownership
        result = frappe.db.sql("""
            SELECT COALESCE(insurance_premium_monthly, 0) as insurance_cost
            FROM `tabVehicle Ownership`
            WHERE vehicle = %s
            AND start_date <= %s
            AND (end_date IS NULL OR end_date >= %s)
            ORDER BY start_date DESC
            LIMIT 1
        """, (vehicle, to_date, from_date))
        
        if result:
            monthly_cost = flt(result[0][0])
            days = date_diff(to_date, from_date) + 1
            return monthly_cost * (days / 30)
        
        return 0
    
    def get_depreciation_cost(self, vehicle, from_date, to_date):
        """Get depreciation cost for vehicle in date range"""
        result = frappe.db.sql("""
            SELECT COALESCE(monthly_depreciation, 0) as depreciation
            FROM `tabVehicle Ownership`
            WHERE vehicle = %s
            AND start_date <= %s
            AND (end_date IS NULL OR end_date >= %s)
            ORDER BY start_date DESC
            LIMIT 1
        """, (vehicle, to_date, from_date))
        
        if result:
            monthly_cost = flt(result[0][0])
            days = date_diff(to_date, from_date) + 1
            return monthly_cost * (days / 30)
        
        return 0
    
    def get_registration_cost(self, vehicle, from_date, to_date):
        """Get registration cost for vehicle in date range"""
        # Placeholder - would integrate with registration module
        return 0
    
    def get_driver_salary(self, driver, from_date, to_date):
        """Get driver salary for date range"""
        salary = frappe.db.get_value("Fleet Driver", driver, "monthly_salary")
        if salary:
            days = date_diff(to_date, from_date) + 1
            return flt(salary) * (days / 30)
        return 0
    
    def get_driver_allowances(self, driver, from_date, to_date):
        """Get driver allowances for date range"""
        # Placeholder - would integrate with payroll module
        return 0
    
    def get_overtime_cost(self, driver, from_date, to_date):
        """Get overtime cost for driver in date range"""
        # Placeholder - would integrate with payroll module
        return 0
    
    def get_bonus_cost(self, driver, from_date, to_date):
        """Get bonus cost for driver in date range"""
        # Placeholder - would integrate with payroll module
        return 0
    
    def get_penalty_cost(self, driver, from_date, to_date):
        """Get penalty cost for driver in date range"""
        # Placeholder - would integrate with penalty module
        return 0
    
    def get_distance_traveled(self, vehicle, from_date, to_date):
        """Get distance traveled by vehicle in date range"""
        readings = frappe.db.sql("""
            SELECT odometer_reading
            FROM `tabFuel Entry`
            WHERE vehicle = %s
            AND fuel_date BETWEEN %s AND %s
            AND docstatus = 1
            ORDER BY fuel_date
        """, (vehicle, from_date, to_date))
        
        if len(readings) >= 2:
            return max(0, flt(readings[-1][0]) - flt(readings[0][0]))
        
        return 0
    
    def get_active_days(self, vehicle, from_date, to_date):
        """Get active days for vehicle in date range"""
        result = frappe.db.sql("""
            SELECT COUNT(DISTINCT DATE(shift_date)) as active_days
            FROM `tabFleet Shift`
            WHERE vehicle = %s
            AND shift_date BETWEEN %s AND %s
            AND docstatus = 1
        """, (vehicle, from_date, to_date))
        
        return flt(result[0][0]) if result else 0
    
    def get_hours_worked(self, driver, from_date, to_date):
        """Get hours worked by driver in date range"""
        result = frappe.db.sql("""
            SELECT SUM(TIMESTAMPDIFF(HOUR, shift_start_time, shift_end_time)) as hours_worked
            FROM `tabFleet Shift`
            WHERE driver = %s
            AND shift_date BETWEEN %s AND %s
            AND docstatus = 1
        """, (driver, from_date, to_date))
        
        return flt(result[0][0]) if result else 0
    
    def get_total_fuel_consumed(self, vehicle, from_date, to_date):
        """Get total fuel consumed by vehicle in date range"""
        result = frappe.db.sql("""
            SELECT SUM(quantity_liters) as total_fuel
            FROM `tabFuel Entry`
            WHERE vehicle = %s
            AND fuel_date BETWEEN %s AND %s
            AND docstatus = 1
        """, (vehicle, from_date, to_date))
        
        return flt(result[0][0]) if result else 0