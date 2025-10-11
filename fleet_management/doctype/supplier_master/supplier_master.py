# Copyright (c) 2025, AFMCOltd (afm@afmcoltd.com)
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class SupplierMaster(Document):
    def validate(self):
        """Validate supplier data before saving"""
        self.validate_supplier_code()
        self.validate_contact_info()
        self.clean_text_fields()
    
    def validate_supplier_code(self):
        """Ensure supplier code is unique and properly formatted"""
        if self.supplier_code:
            self.supplier_code = self.supplier_code.strip().upper()
            
            # Check for duplicate supplier codes
            existing = frappe.db.get_value(
                "Supplier Master", 
                {"supplier_code": self.supplier_code, "name": ["!=", self.name]}, 
                "name"
            )
            if existing:
                frappe.throw(_("Supplier Code {0} already exists").format(self.supplier_code))
    
    def validate_contact_info(self):
        """Validate required contact information"""
        if not self.contact_person:
            frappe.throw(_("Contact Person is required"))
        
        if not self.phone:
            frappe.throw(_("Phone Number is required"))
        
        # Validate email format if provided
        if self.email:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, self.email):
                frappe.throw(_("Please enter a valid email address"))
    
    def clean_text_fields(self):
        """Clean and format text fields"""
        if self.supplier_name_ar:
            self.supplier_name_ar = self.supplier_name_ar.strip()
        
        if self.supplier_name_en:
            self.supplier_name_en = self.supplier_name_en.strip()
        
        if self.contact_person:
            self.contact_person = self.contact_person.strip()
    
    def before_save(self):
        """Actions to perform before saving the document"""
        # Set title field for better display
        if self.supplier_name_en:
            self.title = self.supplier_name_en
        elif self.supplier_name_ar:
            self.title = self.supplier_name_ar
    
    def on_update(self):
        """Actions to perform after updating the document"""
        # Log supplier status changes
        if self.has_value_changed('status'):
            frappe.log_error(
                f"Supplier {self.supplier_code} status changed to {self.status}",
                "Supplier Status Change"
            )