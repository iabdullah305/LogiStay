# Copyright (c) 2025, AFMCOltd (afm@afmcoltd.com)
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class VehicleOwnership(Document):
    def validate(self):
        """Validate vehicle ownership data before saving"""
        self.validate_dates()
        self.validate_vehicle_uniqueness()
        self.validate_lease_information()
        self.set_defaults()
    
    def validate_dates(self):
        """Validate ownership and lease dates"""
        if self.end_date and self.start_date:
            if self.start_date >= self.end_date:
                frappe.throw(_("End Date must be after Start Date"))
        
        # Validate lease dates if applicable
        if self.ownership_type in ["Leased", "Rented"] and self.lease_start_date and self.lease_end_date:
            if self.lease_start_date >= self.lease_end_date:
                frappe.throw(_("Lease End Date must be after Lease Start Date"))
            
            # Ensure lease dates align with ownership dates
            if self.lease_start_date < self.start_date:
                frappe.throw(_("Lease Start Date cannot be before Ownership Start Date"))
            
            if self.end_date and self.lease_end_date > self.end_date:
                frappe.throw(_("Lease End Date cannot be after Ownership End Date"))
    
    def validate_vehicle_uniqueness(self):
        """Ensure no overlapping active ownership for the same vehicle"""
        if self.status == "Active":
            overlapping = frappe.db.sql("""
                SELECT name FROM `tabVehicle Ownership`
                WHERE vehicle = %s 
                AND name != %s
                AND status = 'Active'
                AND (
                    (start_date <= %s AND (end_date IS NULL OR end_date >= %s)) OR
                    (start_date <= %s AND (end_date IS NULL OR end_date >= %s)) OR
                    (start_date >= %s AND (end_date IS NULL OR end_date <= %s))
                )
            """, (self.vehicle, self.name or '', 
                  self.start_date, self.start_date,
                  self.end_date or '2099-12-31', self.end_date or '2099-12-31',
                  self.start_date, self.end_date or '2099-12-31'))
            
            if overlapping:
                frappe.throw(_("Another active ownership record exists for this vehicle during the specified period"))
    
    def validate_lease_information(self):
        """Validate lease/rental specific information"""
        if self.ownership_type in ["Leased", "Rented"]:
            if not self.supplier:
                frappe.throw(_("Supplier is required for leased/rented vehicles"))
            
            if not self.monthly_lease_amount:
                frappe.throw(_("Monthly lease amount is required for leased/rented vehicles"))
            
            if not self.lease_start_date:
                frappe.throw(_("Lease start date is required for leased/rented vehicles"))
        
        # Validate financial information for owned vehicles
        if self.ownership_type == "Company Owned":
            if not self.purchase_price:
                frappe.throw(_("Purchase price is required for company owned vehicles"))
    
    def set_defaults(self):
        """Set default values"""
        if not self.creation_date:
            self.creation_date = frappe.utils.today()
        
        if not self.created_by:
            self.created_by = frappe.session.user
        
        # Set default status
        if not self.status:
            self.status = "Active"
    
    def before_save(self):
        """Actions to perform before saving"""
        self.update_audit_fields()
        self.calculate_depreciation()
    
    def update_audit_fields(self):
        """Update audit trail fields"""
        self.last_updated_by = frappe.session.user
        self.last_update_date = frappe.utils.today()
    
    def calculate_depreciation(self):
        """Calculate current value based on depreciation"""
        if (self.ownership_type == "Company Owned" and 
            self.purchase_price and 
            self.depreciation_rate and 
            self.registration_date):
            
            from datetime import datetime
            
            # Calculate years since purchase
            purchase_date = frappe.utils.getdate(self.registration_date)
            current_date = frappe.utils.getdate()
            years_elapsed = (current_date - purchase_date).days / 365.25
            
            # Calculate depreciated value
            depreciation_factor = (1 - (self.depreciation_rate / 100)) ** years_elapsed
            self.current_value = self.purchase_price * depreciation_factor
    
    def on_update(self):
        """Actions to perform after updating"""
        # Update vehicle ownership status in Fleet Vehicle
        self.update_vehicle_ownership_status()
    
    def update_vehicle_ownership_status(self):
        """Update the ownership status in the linked Fleet Vehicle"""
        if self.vehicle and self.status == "Active":
            frappe.db.set_value("Fleet Vehicle", self.vehicle, {
                "ownership_type": self.ownership_type,
                "owner_name": self.owner_name
            })
    
    def get_monthly_cost(self):
        """Calculate monthly ownership cost"""
        monthly_cost = 0
        
        if self.ownership_type in ["Leased", "Rented"] and self.monthly_lease_amount:
            monthly_cost = self.monthly_lease_amount
        elif self.ownership_type == "Company Owned" and self.monthly_payment:
            monthly_cost = self.monthly_payment
        
        return monthly_cost
    
    def is_lease_expiring_soon(self, days=30):
        """Check if lease is expiring within specified days"""
        if (self.ownership_type in ["Leased", "Rented"] and 
            self.lease_end_date and 
            self.status == "Active"):
            
            from datetime import datetime, timedelta
            
            expiry_date = frappe.utils.getdate(self.lease_end_date)
            warning_date = frappe.utils.getdate() + timedelta(days=days)
            
            return expiry_date <= warning_date
        
        return False