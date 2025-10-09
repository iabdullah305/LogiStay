# Copyright (c) 2024, Fleet Management and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now


class SupervisorDailyTask(Document):
	def validate(self):
		"""Validate task data"""
		self.validate_dates()
		self.validate_room_accommodation()
	
	def validate_dates(self):
		"""Validate task dates"""
		if self.due_date and self.task_date and self.due_date < self.task_date:
			frappe.throw("Due date cannot be earlier than task date")
	
	def validate_room_accommodation(self):
		"""Validate room belongs to selected accommodation"""
		if self.room and self.accommodation:
			room_doc = frappe.get_doc("Room", self.room)
			if room_doc.accommodation != self.accommodation:
				frappe.throw(f"Room {self.room} does not belong to accommodation {self.accommodation}")
	
	def on_update(self):
		"""Update completion date when status changes to completed"""
		if self.status == "Completed" and not self.completed_date:
			self.completed_date = now()
			self.save()
	
	def mark_completed(self, completion_notes=None, completion_status="Satisfactory"):
		"""Mark task as completed"""
		self.status = "Completed"
		self.completed_date = now()
		if completion_notes:
			self.completion_notes = completion_notes
		self.completion_status = completion_status
		self.save()
		
		frappe.msgprint(f"Task {self.name} marked as completed")
	
	def get_overdue_tasks(self):
		"""Get overdue tasks for reporting"""
		from frappe.utils import getdate, today
		
		return frappe.get_all("Supervisor Daily Task",
			filters={
				"status": ["not in", ["Completed", "Cancelled"]],
				"due_date": ["<", today()]
			},
			fields=["name", "task_description", "supervisor", "due_date", "priority"]
		)