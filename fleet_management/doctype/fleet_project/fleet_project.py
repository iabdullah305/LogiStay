# Copyright (c) 2025, AFMCO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FleetProject(Document):
    def validate(self):
        """Validate Fleet Project document"""
        self.validate_project_names()
        self.validate_city_exists()
    
    def validate_project_names(self):
        """Validate project names are provided"""
        name_ar = getattr(self, 'name_ar', None)
        name_en = getattr(self, 'name_en', None)
        
        if not name_ar:
            frappe.throw("Arabic project name is required")
        
        if name_en and name_ar == name_en:
            frappe.msgprint("Arabic and English names are the same", alert=True)
    
    def validate_city_exists(self):
        """Validate that the selected city exists"""
        fleet_city = getattr(self, 'fleet_city', None)
        
        if fleet_city and not frappe.db.exists("Fleet City", fleet_city):
            frappe.throw(f"City '{fleet_city}' does not exist")
    
    def before_save(self):
        """Set title before saving"""
        self.set_title()
    
    def set_title(self):
        """Set document title"""
        name_ar = getattr(self, 'name_ar', None)
        name_en = getattr(self, 'name_en', None)
        
        if name_ar:
            self.title = name_en if name_en else name_ar
    
    def on_update(self):
        """Update related branches when project is updated"""
        self.update_related_branches()
    
    def update_related_branches(self):
        """Update related Fleet Branch documents"""
        name_ar = getattr(self, 'name_ar', None)
        
        if name_ar:
            branches = frappe.get_all("Fleet Branch", 
                                    filters={"fleet_project": name_ar},
                                    fields=["name"])
            
            for branch in branches:
                branch_doc = frappe.get_doc("Fleet Branch", branch.name)
                branch_doc.save()
