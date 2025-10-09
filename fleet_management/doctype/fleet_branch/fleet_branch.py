# Copyright (c) 2025, AFMCO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FleetBranch(Document):
    def validate(self):
        """Validate Fleet Branch document"""
        self.validate_coordinates()
        self.validate_branch_name()
    
    def validate_coordinates(self):
        """Validate GPS coordinates if provided"""
        lat = getattr(self, 'lat', None)
        lng = getattr(self, 'lng', None)
        
        if lat and (lat < -90 or lat > 90):
            frappe.throw("Latitude must be between -90 and 90 degrees")
        
        if lng and (lng < -180 or lng > 180):
            frappe.throw("Longitude must be between -180 and 180 degrees")
    
    def validate_branch_name(self):
        """Validate branch name uniqueness within project"""
        branch_name = getattr(self, 'branch_name', None)
        fleet_project = getattr(self, 'fleet_project', None)
        
        if branch_name and fleet_project:
            existing = frappe.db.exists("Fleet Branch", {
                "branch_name": branch_name,
                "fleet_project": fleet_project,
                "name": ["!=", self.name]
            })
            if existing:
                frappe.throw(f"Branch name '{branch_name}' already exists in project '{fleet_project}'")
    
    def before_save(self):
        """Set title before saving"""
        self.set_title()
    
    def set_title(self):
        """Set document title"""
        branch_name = getattr(self, 'branch_name', None)
        if branch_name:
            self.title = branch_name
