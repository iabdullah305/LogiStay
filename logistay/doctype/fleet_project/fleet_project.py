# Copyright (c) 2025, Fleet Management and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FleetProject(Document):
	def validate(self):
		"""Validate Fleet Project data before saving"""
		self.validate_project_names()
		self.validate_city_exists()
	
	def validate_project_names(self):
		"""Validate project name requirements"""
		if not self.name_ar:
			frappe.throw("Arabic project name is required")
		
		# Check for duplicate Arabic names
		existing = frappe.db.exists("Fleet Project", {
			"name_ar": self.name_ar,
			"name": ["!=", self.name]
		})
		if existing:
			frappe.throw(f"Project with Arabic name '{self.name_ar}' already exists")
	
	def validate_city_exists(self):
		"""Validate that the selected city exists and is active"""
		if self.fleet_city:
			city_doc = frappe.get_doc("Fleet City", self.fleet_city)
			if not city_doc.get("active", True):
				frappe.throw(f"Selected city '{self.fleet_city}' is not active")
	
	def before_save(self):
		"""Actions to perform before saving the document"""
		self.set_title()
	
	def set_title(self):
		"""Set document title for better identification"""
		if self.name_ar:
			self.title = self.name_ar
			if self.name_en:
				self.title += f" ({self.name_en})"
	
	def on_update(self):
		"""Actions to perform after updating the document"""
		self.update_related_branches()
	
	def update_related_branches(self):
		"""Update related branches when project is deactivated"""
		if not self.get("active", True):
			# Deactivate all branches under this project
			branches = frappe.get_all("Fleet Branch", 
				filters={"fleet_project": self.name},
				fields=["name"]
			)
			for branch in branches:
				branch_doc = frappe.get_doc("Fleet Branch", branch.name)
				if hasattr(branch_doc, 'active'):
					branch_doc.active = 0
					branch_doc.save()