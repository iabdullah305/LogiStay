# Copyright (c) 2024, Fleet Management and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class InspectionChecklistItem(Document):
	def validate(self):
		"""Validate checklist item data"""
		if self.status == "Fail" and not self.remarks:
			frappe.throw("Remarks are required for failed inspection items")