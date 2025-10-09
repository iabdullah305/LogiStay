# Copyright (c) 2024, Fleet Management and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Room(Document):
	def validate(self):
		"""Validate room data"""
		self.update_status()
	
	def update_status(self):
		"""Update room status based on occupancy"""
		if not self.name:
			return
		
		# Count active assignments for this room
		active_assignments = frappe.db.count("Employee Accommodation Assignment", {
			"room": self.name,
			"assignment_status": "Active"
		})
		
		# Determine room status based on capacity and assignments
		if active_assignments == 0:
			self.status = "Vacant"
		elif active_assignments < (self.room_capacity or 1):
			self.status = "Partially Occupied"
		else:
			self.status = "Full"
	
	def on_update(self):
		"""Update accommodation occupancy when room is updated"""
		if self.accommodation:
			accommodation_doc = frappe.get_doc("Accommodation", self.accommodation)
			accommodation_doc.calculate_occupancy()
			accommodation_doc.save(ignore_permissions=True)