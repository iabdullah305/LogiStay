import frappe
from frappe.model.document import Document

class FleetDriver(Document):
    def before_save(self):
        if self.is_new():
            self.status = 'Active'