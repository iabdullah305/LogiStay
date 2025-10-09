# Copyright (c) 2024, Fleet Management and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Accommodation(Document):
	def validate(self):
		"""Validate accommodation data"""
		self.calculate_occupancy()
		self.validate_dates()
	
	def calculate_occupancy(self):
		"""Calculate current occupancy based on active assignments"""
		if not self.name:
			return
		
		# Count active employee assignments for this accommodation
		occupancy = frappe.db.count("Employee Accommodation Assignment", {
			"accommodation": self.name,
			"assignment_status": "Active"
		})
		
		self.accommodation_occupancy = occupancy
	
	def validate_dates(self):
		"""Validate contract dates"""
		if self.contract_start_date and self.contract_end_date:
			if self.contract_start_date > self.contract_end_date:
				frappe.throw("Contract Start Date cannot be after Contract End Date")
	
	def on_update(self):
		"""Update room statuses when accommodation is updated"""
		self.update_room_statuses()
	
	def update_room_statuses(self):
		"""Update room statuses based on occupancy"""
		if not self.name:
			return
		
		# Get all rooms for this accommodation
		rooms = frappe.get_all("Room", 
			filters={"accommodation": self.name},
			fields=["name", "room_capacity"]
		)
		
		for room in rooms:
			# Count active assignments for this room
			active_assignments = frappe.db.count("Employee Accommodation Assignment", {
				"room": room.name,
				"assignment_status": "Active"
			})
			
			# Determine room status
			if active_assignments == 0:
				status = "Vacant"
			elif active_assignments < room.room_capacity:
				status = "Partially Occupied"
			else:
				status = "Full"
			
			# Update room status
			frappe.db.set_value("Room", room.name, "status", status)