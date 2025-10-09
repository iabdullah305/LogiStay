# Copyright (c) 2025, AFMCOltd (afm@afmcoltd.com)
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from datetime import datetime, timedelta


class SupplierContract(Document):
    def validate(self):
        """Validate contract data before saving"""
        self.validate_dates()
        self.validate_pricing()
        self.validate_contact_info()
        self.set_defaults()
    
    def validate_dates(self):
        """Validate contract start and end dates"""
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                frappe.throw(_("End Date must be after Start Date"))
            
            # Check for overlapping contracts with same supplier and type
            overlapping = frappe.db.sql("""
                SELECT name FROM `tabSupplier Contract`
                WHERE supplier = %s 
                AND contract_type = %s
                AND name != %s
                AND status IN ('Active', 'Draft')
                AND (
                    (start_date <= %s AND end_date >= %s) OR
                    (start_date <= %s AND end_date >= %s) OR
                    (start_date >= %s AND end_date <= %s)
                )
            """, (self.supplier, self.contract_type, self.name or '', 
                  self.start_date, self.start_date,
                  self.end_date, self.end_date,
                  self.start_date, self.end_date))
            
            if overlapping:
                frappe.throw(_("Overlapping contract exists for this supplier and contract type"))
    
    def validate_pricing(self):
        """Validate pricing information"""
        if not self.base_rate or self.base_rate <= 0:
            frappe.throw(_("Base Rate must be greater than 0"))
        
        # Validate overtime rates are not less than base rate
        if self.overtime_rate and self.overtime_rate < self.base_rate:
            frappe.throw(_("Overtime Rate should not be less than Base Rate"))
        
        if self.holiday_rate and self.holiday_rate < self.base_rate:
            frappe.throw(_("Holiday Rate should not be less than Base Rate"))
        
        if self.night_shift_rate and self.night_shift_rate < self.base_rate:
            frappe.throw(_("Night Shift Rate should not be less than Base Rate"))
    
    def validate_contact_info(self):
        """Validate contact information"""
        if self.contact_email:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, self.contact_email):
                frappe.throw(_("Please enter a valid contact email address"))
    
    def set_defaults(self):
        """Set default values"""
        if not self.creation_date:
            self.creation_date = frappe.utils.today()
        
        if not self.created_by:
            self.created_by = frappe.session.user
        
        if not self.currency:
            self.currency = frappe.get_cached_value("Company", frappe.defaults.get_user_default("Company"), "default_currency")
    
    def before_save(self):
        """Actions to perform before saving"""
        # Auto-update status based on dates
        self.update_status_based_on_dates()
    
    def update_status_based_on_dates(self):
        """Update contract status based on current date and contract dates"""
        today = frappe.utils.getdate()
        
        if self.start_date and self.end_date:
            if today < self.start_date:
                if self.status not in ['Draft']:
                    self.status = 'Draft'
            elif self.start_date <= today <= self.end_date:
                if self.status not in ['Active', 'Terminated']:
                    self.status = 'Active'
            elif today > self.end_date:
                if self.status not in ['Expired', 'Renewed', 'Terminated']:
                    self.status = 'Expired'
    
    def on_update(self):
        """Actions to perform after updating"""
        # Send notifications for status changes
        if self.has_value_changed('status'):
            self.send_status_notification()
    
    def send_status_notification(self):
        """Send notification when contract status changes"""
        try:
            # Get users with Fleet Manager role
            fleet_managers = frappe.get_all("Has Role", 
                filters={"role": "Fleet Manager"}, 
                fields=["parent"]
            )
            
            for manager in fleet_managers:
                frappe.sendmail(
                    recipients=[manager.parent],
                    subject=f"Contract Status Update: {self.contract_title}",
                    message=f"""
                    Contract {self.name} status has been updated to {self.status}.
                    
                    Contract Details:
                    - Title: {self.contract_title}
                    - Supplier: {self.supplier}
                    - Type: {self.contract_type}
                    - Start Date: {self.start_date}
                    - End Date: {self.end_date}
                    """
                )
        except Exception as e:
            frappe.log_error(f"Failed to send contract notification: {str(e)}")
    
    def get_active_rate(self, rate_type="base"):
        """Get active rate for different types"""
        rate_map = {
            "base": self.base_rate,
            "overtime": self.overtime_rate or self.base_rate,
            "holiday": self.holiday_rate or self.base_rate,
            "night_shift": self.night_shift_rate or self.base_rate
        }
        return rate_map.get(rate_type, self.base_rate)