# Copyright (c) 2025, Fleet Management and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FleetBranch(Document):
	def validate(self):
		"""Validate Fleet Branch data before saving"""
		self.validate_coordinates()
		self.validate_branch_name()
	
	def validate_coordinates(self):
		"""Validate latitude and longitude coordinates"""
		if self.lat and (self.lat < -90 or self.lat > 90):
			frappe.throw("Latitude must be between -90 and 90 degrees")
		
		if self.lng and (self.lng < -180 or self.lng > 180):
			frappe.throw("Longitude must be between -180 and 180 degrees")
	
	def validate_branch_name(self):
		"""Validate branch name uniqueness within project"""
		if self.fleet_project:
			existing = frappe.db.exists("Fleet Branch", {
				"branch_name": self.branch_name,
				"fleet_project": self.fleet_project,
				"name": ["!=", self.name]
			})
			if existing:
				frappe.throw(f"Branch name '{self.branch_name}' already exists in project '{self.fleet_project}'")
	
	def before_save(self):
		"""Actions to perform before saving the document"""
		self.set_title()
	
	def set_title(self):
		"""Set document title for better identification"""
		if self.branch_name and self.fleet_project:
			self.title = f"{self.branch_name} - {self.fleet_project}"