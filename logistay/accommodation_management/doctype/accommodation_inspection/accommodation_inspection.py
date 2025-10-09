# Copyright (c) 2024, Fleet Management and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class AccommodationInspection(Document):
	def validate(self):
		"""Validate inspection data"""
		self.validate_inspection_date()
		self.validate_status_change()
	
	def validate_inspection_date(self):
		"""Validate inspection date is not in future"""
		if self.inspection_date and self.inspection_date > today():
			frappe.throw("Inspection Date cannot be in the future")
	
	def validate_status_change(self):
		"""Validate status changes"""
		if self.status == "Approved" and not self.inspection_checklist:
			frappe.throw("Cannot approve inspection without checklist items")
	
	def on_submit(self):
		"""Actions when inspection is submitted"""
		self.status = "Submitted"
	
	def approve_inspection(self):
		"""Approve the inspection"""
		if self.status != "Submitted":
			frappe.throw("Only submitted inspections can be approved")
		
		self.status = "Approved"
		self.save()
		
	def get_failed_items(self):
		"""Get list of failed checklist items"""
		failed_items = []
		for item in self.inspection_checklist:
			if item.status == "Fail":
				failed_items.append(item)
		return failed_items