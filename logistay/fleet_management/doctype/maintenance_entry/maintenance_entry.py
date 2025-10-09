# Copyright (c) 2024, Fleet Management and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MaintenanceEntry(Document):
	def validate(self):
		"""Validate maintenance entry data"""
		if self.cost and self.cost < 0:
			frappe.throw("Maintenance cost cannot be negative")