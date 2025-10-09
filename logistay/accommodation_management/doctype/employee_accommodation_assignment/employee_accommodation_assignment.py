# Copyright (c) 2024, Fleet Management and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EmployeeAccommodationAssignment(Document):
	def validate(self):
		"""Validate assignment data"""
		self.set_accommodation_from_room()
		self.validate_dates()
		self.validate_room_capacity()
	
	def set_accommodation_from_room(self):
		"""Set accommodation based on selected room"""
		if self.room:
			room_doc = frappe.get_doc("Room", self.room)
			self.accommodation = room_doc.accommodation
	
	def validate_dates(self):
		"""Validate check-in and check-out dates"""
		if self.check_in_date and self.check_out_date:
			if self.check_in_date > self.check_out_date:
				frappe.throw("Check In Date cannot be after Check Out Date")
	
	def validate_room_capacity(self):
		"""Validate that room has capacity for new assignment"""
		if not self.room or self.assignment_status != "Active":
			return
		
		# Count existing active assignments for this room (excluding current if updating)
		filters = {
			"room": self.room,
			"assignment_status": "Active"
		}
		
		if self.name:  # If updating existing record
			filters["name"] = ["!=", self.name]
		
		active_assignments = frappe.db.count("Employee Accommodation Assignment", filters)
		
		# Get room capacity
		room_capacity = frappe.db.get_value("Room", self.room, "room_capacity") or 1
		
		if active_assignments >= room_capacity:
			frappe.throw(f"Room {self.room} is at full capacity ({room_capacity} employees)")
	
	def on_update(self):
		"""Update room and accommodation status when assignment is updated"""
		if self.room:
			# Update room status
			room_doc = frappe.get_doc("Room", self.room)
			room_doc.update_status()
			room_doc.save(ignore_permissions=True)
			
			# Update accommodation occupancy
			if room_doc.accommodation:
				accommodation_doc = frappe.get_doc("Accommodation", room_doc.accommodation)
				accommodation_doc.calculate_occupancy()
				accommodation_doc.save(ignore_permissions=True)