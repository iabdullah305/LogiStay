# Copyright (c) 2025, AFMCOltd (afm@afmcoltd.com)
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class FleetCity(Document):
    def validate(self):
        self.name_ar = self.name_ar.strip() if self.name_ar else ""
        self.name_en = self.name_en.strip() if self.name_en else ""