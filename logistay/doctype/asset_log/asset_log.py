# Copyright (c) 2024, Fleet Management and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AssetLog(Document):
	def validate(self):
		"""Validate asset log data"""
		self.validate_unique_asset_code()
	
	def validate_unique_asset_code(self):
		"""Ensure asset code is unique"""
		if not self.asset_code:
			return
		
		# Check for duplicate asset codes
		existing = frappe.db.get_value("Asset Log", 
			{"asset_code": self.asset_code, "name": ["!=", self.name or ""]}, 
			"name"
		)
		
		if existing:
			frappe.throw(f"Asset Code {self.asset_code} already exists in {existing}")
	
	def add_maintenance_entry(self, maintenance_date, description, cost=0, performed_by=""):
		"""Add a maintenance entry to the log"""
		self.append("maintenance_log", {
			"maintenance_date": maintenance_date,
			"description": description,
			"cost": cost,
			"performed_by": performed_by
		})
		self.save()
		
	def get_total_maintenance_cost(self):
		"""Calculate total maintenance cost"""
		total = 0
		for entry in self.maintenance_log:
			if entry.cost:
				total += entry.cost
		return total