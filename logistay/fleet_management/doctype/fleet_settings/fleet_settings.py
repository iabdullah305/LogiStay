# Copyright (c) 2025, AFMCOltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from typing import Optional


class FleetSettings(Document):
	"""
	Fleet Settings - Single DocType for system-wide fleet management configuration

	This DocType manages all configurable settings for the fleet management system,
	including fuel limits, trip settings, maintenance configuration, and notifications.
	"""

	def validate(self):
		"""Validate settings before saving"""
		self.validate_fuel_settings()
		self.validate_trip_settings()
		self.validate_maintenance_settings()
		self.validate_driver_settings()
		self.validate_notification_settings()

	def validate_fuel_settings(self):
		"""Validate fuel management settings"""
		# Validate max fuel quantity
		if self.max_fuel_quantity and self.max_fuel_quantity <= 0:
			frappe.throw(_("Maximum Fuel Quantity must be greater than zero"))

		if self.max_fuel_quantity and self.max_fuel_quantity > 10000:
			frappe.throw(_("Maximum Fuel Quantity seems too high. Please verify."))

		# Validate max fuel amount
		if self.max_fuel_amount and self.max_fuel_amount <= 0:
			frappe.throw(_("Maximum Fuel Amount must be greater than zero"))

		# Validate fuel entry days back
		if self.fuel_entry_max_days_back and self.fuel_entry_max_days_back < 0:
			frappe.throw(_("Fuel Entry Max Days Back cannot be negative"))

		if self.fuel_entry_max_days_back and self.fuel_entry_max_days_back > 365:
			frappe.throw(_("Fuel Entry Max Days Back cannot exceed 365 days"))

		# Validate fuel price alert threshold
		if self.enable_fuel_price_alerts and not self.fuel_price_alert_threshold:
			frappe.throw(_("Fuel Price Alert Threshold is required when alerts are enabled"))

		if self.fuel_price_alert_threshold and self.fuel_price_alert_threshold <= 0:
			frappe.throw(_("Fuel Price Alert Threshold must be greater than zero"))

	def validate_trip_settings(self):
		"""Validate trip management settings"""
		# Validate max trip distance
		if self.max_trip_distance and self.max_trip_distance <= 0:
			frappe.throw(_("Maximum Trip Distance must be greater than zero"))

		if self.max_trip_distance and self.max_trip_distance > 50000:
			frappe.throw(_("Maximum Trip Distance seems too high. Please verify."))

	def validate_maintenance_settings(self):
		"""Validate maintenance settings"""
		# Validate maintenance reminder days
		if self.maintenance_reminder_days and self.maintenance_reminder_days < 0:
			frappe.throw(_("Maintenance Reminder Days cannot be negative"))

		if self.maintenance_reminder_days and self.maintenance_reminder_days > 365:
			frappe.throw(_("Maintenance Reminder Days cannot exceed 365 days"))

	def validate_driver_settings(self):
		"""Validate driver management settings"""
		# Validate license expiry reminder
		if self.license_expiry_reminder_days and self.license_expiry_reminder_days < 0:
			frappe.throw(_("License Expiry Reminder Days cannot be negative"))

		if self.license_expiry_reminder_days and self.license_expiry_reminder_days > 365:
			frappe.throw(_("License Expiry Reminder Days cannot exceed 365 days"))

		# Validate max driving hours
		if self.max_driving_hours_per_day and self.max_driving_hours_per_day <= 0:
			frappe.throw(_("Maximum Driving Hours Per Day must be greater than zero"))

		if self.max_driving_hours_per_day and self.max_driving_hours_per_day > 24:
			frappe.throw(_("Maximum Driving Hours Per Day cannot exceed 24 hours"))

	def validate_notification_settings(self):
		"""Validate notification settings"""
		# Validate notification email
		if self.enable_notifications and self.notification_email:
			import re
			email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
			if not re.match(email_pattern, self.notification_email):
				frappe.throw(_("Invalid notification email address"))

	def on_update(self):
		"""Actions to perform after updating settings"""
		# Clear cache to ensure new settings are applied
		frappe.cache().delete_value("fleet_settings")

		# Log the update
		frappe.logger().info(f"Fleet Settings updated by {frappe.session.user}")


@frappe.whitelist()
def get_fleet_settings() -> dict:
	"""
	Get Fleet Settings singleton document

	Returns:
		dict: Fleet Settings document as dictionary

	Raises:
		frappe.DoesNotExistError: If settings document doesn't exist
	"""
	try:
		# Try to get from cache first
		settings = frappe.cache().get_value("fleet_settings")

		if not settings:
			# Get from database
			if frappe.db.exists("Fleet Settings", "Fleet Settings"):
				settings_doc = frappe.get_single("Fleet Settings")
				settings = settings_doc.as_dict()

				# Cache for 1 hour
				frappe.cache().set_value("fleet_settings", settings, expires_in_sec=3600)
			else:
				# Create default settings if doesn't exist
				settings_doc = frappe.get_doc({
					"doctype": "Fleet Settings"
				})
				settings_doc.insert(ignore_permissions=True)
				settings = settings_doc.as_dict()

		return settings

	except Exception as e:
		frappe.log_error(f"Error getting Fleet Settings: {str(e)}")
		frappe.throw(_("Failed to load Fleet Settings"))


@frappe.whitelist()
def get_setting_value(setting_name: str) -> Optional[any]:
	"""
	Get a specific setting value

	Args:
		setting_name: Name of the setting field

	Returns:
		The value of the requested setting, or None if not found

	Example:
		>>> get_setting_value('max_fuel_quantity')
		500.0
	"""
	try:
		settings = get_fleet_settings()
		return settings.get(setting_name)
	except Exception as e:
		frappe.log_error(f"Error getting setting '{setting_name}': {str(e)}")
		return None


def validate_fuel_entry_against_settings(quantity: float, amount: float, fuel_date: str) -> bool:
	"""
	Validate fuel entry against Fleet Settings

	Args:
		quantity: Fuel quantity in liters
		amount: Fuel amount
		fuel_date: Date of fuel entry

	Returns:
		bool: True if valid, raises exception if invalid

	Raises:
		frappe.ValidationError: If validation fails
	"""
	from frappe.utils import getdate, add_days

	settings = get_fleet_settings()

	# Check max quantity
	max_quantity = settings.get("max_fuel_quantity", 500)
	if quantity > max_quantity:
		frappe.throw(_(f"Fuel quantity cannot exceed {max_quantity} liters"))

	# Check max amount
	max_amount = settings.get("max_fuel_amount", 100000)
	if amount > max_amount:
		frappe.throw(_(f"Fuel amount cannot exceed {max_amount}"))

	# Check date range
	max_days_back = settings.get("fuel_entry_max_days_back", 90)
	min_allowed_date = add_days(getdate(), -max_days_back)

	if getdate(fuel_date) < min_allowed_date:
		frappe.throw(_(f"Fuel entry date cannot be older than {max_days_back} days"))

	# Check fuel price alert
	if settings.get("enable_fuel_price_alerts"):
		price_per_liter = amount / quantity if quantity > 0 else 0
		threshold = settings.get("fuel_price_alert_threshold", 0)

		if threshold and price_per_liter > threshold:
			frappe.msgprint(
				_(f"Warning: Fuel price per liter ({price_per_liter:.2f}) exceeds threshold ({threshold:.2f})"),
				indicator="orange",
				alert=True
			)

	return True


def validate_trip_distance_against_settings(distance: float) -> bool:
	"""
	Validate trip distance against Fleet Settings

	Args:
		distance: Trip distance in kilometers

	Returns:
		bool: True if valid, raises exception if invalid

	Raises:
		frappe.ValidationError: If validation fails
	"""
	settings = get_fleet_settings()

	max_distance = settings.get("max_trip_distance", 1000)
	if distance > max_distance:
		frappe.throw(_(f"Trip distance cannot exceed {max_distance} kilometers"))

	return True


def send_maintenance_reminders():
	"""
	Background job to send maintenance reminders
	Called by scheduler
	"""
	settings = get_fleet_settings()

	if not settings.get("enable_maintenance_alerts"):
		return

	reminder_days = settings.get("maintenance_reminder_days", 7)

	# Implementation for sending reminders would go here
	# This would be called by a scheduler hook
	frappe.logger().info(f"Maintenance reminders scheduled for {reminder_days} days before due date")


def send_license_expiry_reminders():
	"""
	Background job to send license expiry reminders
	Called by scheduler
	"""
	settings = get_fleet_settings()

	reminder_days = settings.get("license_expiry_reminder_days", 30)

	# Implementation for sending reminders would go here
	# This would be called by a scheduler hook
	frappe.logger().info(f"License expiry reminders scheduled for {reminder_days} days before expiry")
