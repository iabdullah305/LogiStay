# Copyright (c) 2025, AFMCOltd (afm@afmcoltd.com)
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class FuelEntry(Document):
    def validate(self):
        """Validate fuel entry data before saving"""
        self.validate_odometer_reading()
        self.validate_fuel_data()
        self.calculate_totals()
        self.calculate_efficiency()
        self.set_defaults()
    
    def validate_odometer_reading(self):
        """Validate odometer reading against previous entries"""
        if self.vehicle and self.odometer_reading:
            # Get the latest odometer reading for this vehicle
            latest_entry = frappe.db.sql("""
                SELECT odometer_reading, name 
                FROM `tabFuel Entry` 
                WHERE vehicle = %s 
                AND name != %s 
                AND docstatus != 2
                ORDER BY fuel_date DESC, creation DESC 
                LIMIT 1
            """, (self.vehicle, self.name or ''))
            
            if latest_entry:
                latest_reading = latest_entry[0][0]
                if self.odometer_reading < latest_reading:
                    frappe.throw(_("Odometer reading cannot be less than the previous reading of {0} KM").format(latest_reading))
                
                self.previous_odometer = latest_reading
                self.distance_traveled = self.odometer_reading - latest_reading
            else:
                # First entry for this vehicle
                self.previous_odometer = 0
                self.distance_traveled = 0
    
    def validate_fuel_data(self):
        """Validate fuel quantity and pricing"""
        if not self.quantity_liters or self.quantity_liters <= 0:
            frappe.throw(_("Fuel quantity must be greater than 0"))
        
        if not self.price_per_liter or self.price_per_liter <= 0:
            frappe.throw(_("Price per liter must be greater than 0"))
        
        # Validate reasonable fuel quantity (not more than tank capacity)
        if self.quantity_liters > 200:  # Assuming max tank capacity of 200L
            frappe.throw(_("Fuel quantity seems unusually high. Please verify."))
    
    def calculate_totals(self):
        """Calculate total amount and cost per km"""
        if self.quantity_liters and self.price_per_liter:
            self.total_amount = self.quantity_liters * self.price_per_liter
        
        # Calculate cost per km if distance is available
        if self.distance_traveled and self.distance_traveled > 0:
            self.cost_per_km = self.total_amount / self.distance_traveled
    
    def calculate_efficiency(self):
        """Calculate fuel efficiency"""
        if (self.distance_traveled and 
            self.distance_traveled > 0 and 
            self.quantity_liters and 
            self.quantity_liters > 0):
            
            self.fuel_efficiency = self.distance_traveled / self.quantity_liters
    
    def set_defaults(self):
        """Set default values"""
        if not self.creation_date:
            self.creation_date = frappe.utils.today()
        
        if not self.created_by:
            self.created_by = frappe.session.user
        
        if not self.status:
            self.status = "Draft"
        
        if not self.currency:
            self.currency = frappe.get_cached_value("Company", frappe.defaults.get_user_default("Company"), "default_currency")
    
    def before_save(self):
        """Actions to perform before saving"""
        self.update_audit_fields()
        self.calculate_budget_variance()
    
    def update_audit_fields(self):
        """Update audit trail fields"""
        self.last_updated_by = frappe.session.user
        self.last_update_date = frappe.utils.today()
    
    def calculate_budget_variance(self):
        """Calculate budget variance if monthly budget is set"""
        if self.monthly_fuel_budget:
            # Get total fuel cost for current month
            from frappe.utils import getdate, get_first_day, get_last_day
            
            fuel_date = getdate(self.fuel_date)
            month_start = get_first_day(fuel_date)
            month_end = get_last_day(fuel_date)
            
            monthly_spent = frappe.db.sql("""
                SELECT COALESCE(SUM(total_amount), 0)
                FROM `tabFuel Entry`
                WHERE vehicle = %s
                AND fuel_date BETWEEN %s AND %s
                AND name != %s
                AND docstatus != 2
                AND status IN ('Approved', 'Reimbursed')
            """, (self.vehicle, month_start, month_end, self.name or ''))[0][0]
            
            # Add current entry amount
            total_monthly_cost = monthly_spent + (self.total_amount or 0)
            self.budget_variance = total_monthly_cost - self.monthly_fuel_budget
    
    def on_update(self):
        """Actions to perform after updating"""
        # Update vehicle's last fuel date and odometer
        if self.status == "Approved":
            self.update_vehicle_fuel_info()
    
    def update_vehicle_fuel_info(self):
        """Update vehicle's fuel information"""
        if self.vehicle:
            frappe.db.set_value("Fleet Vehicle", self.vehicle, {
                "last_fuel_date": self.fuel_date,
                "current_odometer": self.odometer_reading
            })
    
    def get_fuel_efficiency_trend(self, periods=6):
        """Get fuel efficiency trend for the vehicle"""
        if not self.vehicle:
            return []
        
        efficiency_data = frappe.db.sql("""
            SELECT 
                DATE_FORMAT(fuel_date, '%%Y-%%m') as period,
                AVG(fuel_efficiency) as avg_efficiency,
                COUNT(*) as entries_count
            FROM `tabFuel Entry`
            WHERE vehicle = %s
            AND fuel_efficiency > 0
            AND docstatus != 2
            AND status = 'Approved'
            GROUP BY DATE_FORMAT(fuel_date, '%%Y-%%m')
            ORDER BY period DESC
            LIMIT %s
        """, (self.vehicle, periods), as_dict=True)
        
        return efficiency_data
    
    def validate_duplicate_receipt(self):
        """Check for duplicate receipt numbers"""
        if self.receipt_number:
            duplicate = frappe.db.get_value(
                "Fuel Entry",
                {
                    "receipt_number": self.receipt_number,
                    "fuel_station": self.fuel_station,
                    "name": ["!=", self.name]
                },
                "name"
            )
            
            if duplicate:
                frappe.throw(_("Receipt number {0} already exists for this fuel station").format(self.receipt_number))
    
    def send_approval_notification(self):
        """Send notification for approval"""
        if self.status == "Pending Approval":
            # Get Fleet Managers for approval
            managers = frappe.get_all("Has Role", 
                filters={"role": "Fleet Manager"}, 
                fields=["parent"]
            )
            
            for manager in managers:
                frappe.sendmail(
                    recipients=[manager.parent],
                    subject=f"Fuel Entry Approval Required: {self.name}",
                    message=f"""
                    A fuel entry requires your approval:
                    
                    Vehicle: {self.vehicle}
                    Driver: {self.driver}
                    Amount: {self.total_amount} {self.currency}
                    Date: {self.fuel_date}
                    Quantity: {self.quantity_liters} Liters
                    """
                )