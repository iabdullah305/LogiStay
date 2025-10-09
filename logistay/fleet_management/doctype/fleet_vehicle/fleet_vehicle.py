import frappe
from frappe.model.document import Document

class FleetVehicle(Document):
    def before_save(self):
        if self.is_new():
            self.status = 'Active'