# Copyright (c) 2025, AFMCOltd (afm@afmcoltd.com)
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate


class DriverVehicleAssignment(Document):
    def validate(self):
        """Validate the driver vehicle assignment"""
        self.validate_assignment_dates()
        self.validate_assignment_conflicts()
        self.validate_driver_license_compatibility()
        self.set_audit_fields()
    
    def validate_assignment_dates(self):
        """Validate assignment date ranges"""
        if self.start_date and self.end_date:
            if getdate(self.start_date) > getdate(self.end_date):
                frappe.throw(_("Start Date cannot be after End Date"))
        
        if self.start_date and getdate(self.start_date) < getdate(nowdate()):
            if not frappe.has_permission("Driver Vehicle Assignment", "write"):
                frappe.throw(_("Start Date cannot be in the past"))
    
    def validate_assignment_conflicts(self):
        """Check for conflicting assignments"""
        # Check for overlapping assignments for the same driver-vehicle combination
        filters = {
            "driver": self.driver,
            "vehicle": self.vehicle,
            "status": ["in", ["Active", "Suspended"]],
            "name": ["!=", self.name]
        }
        
        # Build date range conditions
        conditions = []
        if self.start_date:
            conditions.append("(start_date <= '{0}')".format(self.start_date))
        if self.end_date:
            conditions.append("(end_date >= '{0}' OR end_date IS NULL)".format(self.end_date))
        else:
            conditions.append("(end_date IS NULL OR end_date >= '{0}')".format(self.start_date))
        
        if conditions:
            existing_assignments = frappe.db.sql("""
                SELECT name, assignment_role, start_date, end_date
                FROM `tabDriver Vehicle Assignment`
                WHERE driver = %(driver)s 
                AND vehicle = %(vehicle)s
                AND status IN ('Active', 'Suspended')
                AND name != %(name)s
                AND ({conditions})
            """.format(conditions=" AND ".join(conditions)), {
                "driver": self.driver,
                "vehicle": self.vehicle,
                "name": self.name or ""
            }, as_dict=True)
            
            if existing_assignments:
                assignment = existing_assignments[0]
                frappe.throw(_("Driver {0} is already assigned to Vehicle {1} as {2} from {3} to {4}").format(
                    self.driver, self.vehicle, assignment.assignment_role,
                    assignment.start_date, assignment.end_date or "Ongoing"
                ))
        
        # Check for primary role conflicts (only one primary driver per vehicle at a time)
        if self.assignment_role == "Primary":
            primary_assignments = frappe.db.sql("""
                SELECT name, driver, start_date, end_date
                FROM `tabDriver Vehicle Assignment`
                WHERE vehicle = %(vehicle)s
                AND assignment_role = 'Primary'
                AND status IN ('Active', 'Suspended')
                AND name != %(name)s
                AND (
                    (start_date <= %(start_date)s AND (end_date >= %(start_date)s OR end_date IS NULL))
                    OR (%(end_date)s IS NULL OR start_date <= %(end_date)s)
                )
            """, {
                "vehicle": self.vehicle,
                "start_date": self.start_date,
                "end_date": self.end_date,
                "name": self.name or ""
            }, as_dict=True)
            
            if primary_assignments:
                assignment = primary_assignments[0]
                frappe.throw(_("Vehicle {0} already has a Primary driver ({1}) assigned from {2} to {3}").format(
                    self.vehicle, assignment.driver,
                    assignment.start_date, assignment.end_date or "Ongoing"
                ))
    
    def validate_driver_license_compatibility(self):
        """Validate driver license compatibility with vehicle type"""
        if not self.driver or not self.vehicle:
            return
        
        # Get driver license information
        driver_doc = frappe.get_doc("Fleet Driver", self.driver)
        vehicle_doc = frappe.get_doc("Fleet Vehicle", self.vehicle)
        
        # Check if driver has valid license
        if not hasattr(driver_doc, 'license_number') or not driver_doc.license_number:
            frappe.throw(_("Driver {0} does not have a valid license on file").format(self.driver))
        
        # Check license expiry if available
        if hasattr(driver_doc, 'license_expiry_date') and driver_doc.license_expiry_date:
            if getdate(driver_doc.license_expiry_date) < getdate(nowdate()):
                frappe.throw(_("Driver {0}'s license has expired on {1}").format(
                    self.driver, driver_doc.license_expiry_date
                ))
        
        # Check license category compatibility (if available)
        if hasattr(driver_doc, 'license_category') and hasattr(vehicle_doc, 'vehicle_category'):
            if driver_doc.license_category and vehicle_doc.vehicle_category:
                # Define license-vehicle compatibility matrix
                compatibility_matrix = {
                    "Light Vehicle": ["Car", "SUV", "Pickup", "Van"],
                    "Heavy Vehicle": ["Truck", "Bus", "Heavy Equipment"],
                    "Motorcycle": ["Motorcycle", "Scooter"],
                    "Commercial": ["Truck", "Bus", "Commercial Van", "Heavy Equipment"]
                }
                
                compatible_vehicles = compatibility_matrix.get(driver_doc.license_category, [])
                if vehicle_doc.vehicle_category not in compatible_vehicles:
                    frappe.throw(_("Driver {0} with {1} license cannot be assigned to {2} vehicle").format(
                        self.driver, driver_doc.license_category, vehicle_doc.vehicle_category
                    ))
    
    def set_audit_fields(self):
        """Set audit fields for tracking"""
        if not self.created_by:
            self.created_by = frappe.session.user
        if not self.creation_date:
            self.creation_date = frappe.utils.now()
        
        self.modified_by = frappe.session.user
        self.last_modified = frappe.utils.now()
    
    def on_update(self):
        """Actions to perform after update"""
        # Log the assignment change using Frappe's built-in activity log
        frappe.get_doc({
            "doctype": "Activity Log",
            "subject": _("Driver Vehicle Assignment Updated"),
            "content": _("Driver {0} assignment to Vehicle {1} updated as {2}").format(
                self.driver, self.vehicle, self.assignment_role
            ),
            "reference_doctype": self.doctype,
            "reference_name": self.name,
            "user": frappe.session.user
        }).insert(ignore_permissions=True)
    
    def on_cancel(self):
        """Actions to perform on cancellation"""
        self.status = "Terminated"
        
    def get_dashboard_data(self):
        """Return dashboard data for the assignment"""
        return {
            "fieldname": "driver_vehicle_assignment",
            "transactions": [
                {
                    "label": _("Fleet Operations"),
                    "items": ["Fleet Shift", "Fuel Entry"]
                }
            ]
        }


@frappe.whitelist()
def get_available_vehicles(driver, start_date, end_date=None):
    """Get list of vehicles available for assignment to a driver"""
    conditions = ["v.status = 'Active'"]
    values = {"driver": driver, "start_date": start_date}
    
    if end_date:
        values["end_date"] = end_date
        date_condition = """
            AND v.name NOT IN (
                SELECT DISTINCT vehicle 
                FROM `tabDriver Vehicle Assignment` 
                WHERE status IN ('Active', 'Suspended')
                AND assignment_role = 'Primary'
                AND start_date <= %(end_date)s
                AND (end_date >= %(start_date)s OR end_date IS NULL)
            )
        """
    else:
        date_condition = """
            AND v.name NOT IN (
                SELECT DISTINCT vehicle 
                FROM `tabDriver Vehicle Assignment` 
                WHERE status IN ('Active', 'Suspended')
                AND assignment_role = 'Primary'
                AND (end_date >= %(start_date)s OR end_date IS NULL)
            )
        """
    
    query = """
        SELECT v.name, v.vehicle_number, v.make, v.model, v.vehicle_type
        FROM `tabFleet Vehicle` v
        WHERE {conditions} {date_condition}
        ORDER BY v.vehicle_number
    """.format(
        conditions=" AND ".join(conditions),
        date_condition=date_condition
    )
    
    return frappe.db.sql(query, values, as_dict=True)


@frappe.whitelist()
def get_driver_assignments(driver, status=None):
    """Get all assignments for a specific driver"""
    filters = {"driver": driver}
    if status:
        filters["status"] = status
    
    return frappe.get_all(
        "Driver Vehicle Assignment",
        filters=filters,
        fields=["name", "vehicle", "assignment_role", "start_date", "end_date", "status"],
        order_by="start_date desc"
    )