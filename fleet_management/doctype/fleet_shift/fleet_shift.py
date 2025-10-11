# Copyright (c) 2025, AFMCOltd (afm@afmcoltd.com)
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class FleetShift(Document):
    def validate(self):
        self.validate_vehicle_availability()
        self.validate_driver_availability()
    
    def validate_vehicle_availability(self):
        """Check if the vehicle is available for the scheduled shift"""
        existing_shifts = frappe.get_all(
            "Fleet Shift",
            filters={
                "fleet_vehicle": self.fleet_vehicle,
                "shift_date": self.shift_date,
                "shift_type": self.shift_type,
                "status": ["in", ["SCHEDULED", "IN_PROGRESS"]],
                "name": ["!=", self.name]
            }
        )
        
        if existing_shifts:
            frappe.throw(_("Vehicle {0} is already scheduled for {1} shift on {2}").format(
                self.fleet_vehicle, self.shift_type, self.shift_date
            ))
    
    def validate_driver_availability(self):
        """Check if the driver is available for the scheduled shift"""
        existing_shifts = frappe.get_all(
            "Fleet Shift",
            filters={
                "fleet_driver": self.fleet_driver,
                "shift_date": self.shift_date,
                "shift_type": self.shift_type,
                "status": ["in", ["SCHEDULED", "IN_PROGRESS"]],
                "name": ["!=", self.name]
            }
        )
        
        if existing_shifts:
            frappe.throw(_("Driver {0} is already scheduled for {1} shift on {2}").format(
                self.fleet_driver, self.shift_type, self.shift_date
            ))
    
    def on_submit(self):
        """Update status to SCHEDULED when submitted"""
        self.status = "SCHEDULED"
    
    def on_cancel(self):
        """Update status to CANCELLED when cancelled"""
        self.status = "CANCELLED"