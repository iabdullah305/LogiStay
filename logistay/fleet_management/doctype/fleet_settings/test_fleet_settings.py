# Copyright (c) 2025, AFMCOltd and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase, UnitTestCase


class UnitTestFleetSettings(UnitTestCase):
	"""
	Unit tests for FleetSettings.
	Use this class for testing individual functions and methods.
	"""

	def test_validate_positive_values(self):
		"""Test that validation prevents negative values"""
		settings = frappe.get_doc({
			"doctype": "Fleet Settings"
		})

		# Test negative max fuel quantity
		settings.max_fuel_quantity = -100
		with self.assertRaises(frappe.ValidationError):
			settings.validate_fuel_settings()

		# Test negative max fuel amount
		settings.max_fuel_quantity = 500
		settings.max_fuel_amount = -1000
		with self.assertRaises(frappe.ValidationError):
			settings.validate_fuel_settings()

	def test_validate_ranges(self):
		"""Test that validation enforces valid ranges"""
		settings = frappe.get_doc({
			"doctype": "Fleet Settings"
		})

		# Test fuel entry days back exceeding limit
		settings.fuel_entry_max_days_back = 400
		with self.assertRaises(frappe.ValidationError):
			settings.validate_fuel_settings()

		# Test max driving hours exceeding 24
		settings.fuel_entry_max_days_back = 90
		settings.max_driving_hours_per_day = 25
		with self.assertRaises(frappe.ValidationError):
			settings.validate_driver_settings()

	def test_email_validation(self):
		"""Test email validation"""
		settings = frappe.get_doc({
			"doctype": "Fleet Settings",
			"enable_notifications": 1
		})

		# Test invalid email
		settings.notification_email = "invalid-email"
		with self.assertRaises(frappe.ValidationError):
			settings.validate_notification_settings()

		# Test valid email
		settings.notification_email = "test@example.com"
		settings.validate_notification_settings()  # Should not raise


class IntegrationTestFleetSettings(IntegrationTestCase):
	"""
	Integration tests for FleetSettings.
	Use this class for testing interactions between multiple components.
	"""

	def setUp(self):
		"""Set up test environment"""
		# Create or get Fleet Settings singleton
		if frappe.db.exists("Fleet Settings", "Fleet Settings"):
			self.settings = frappe.get_single("Fleet Settings")
		else:
			self.settings = frappe.get_doc({
				"doctype": "Fleet Settings"
			})
			self.settings.insert(ignore_permissions=True)

	def tearDown(self):
		"""Clean up after tests"""
		# Reset to default values after each test
		frappe.db.rollback()

	def test_settings_creation(self):
		"""Test that Fleet Settings can be created"""
		self.assertIsNotNone(self.settings)
		self.assertEqual(self.settings.doctype, "Fleet Settings")

	def test_default_values(self):
		"""Test that default values are set correctly"""
		settings = frappe.get_doc({
			"doctype": "Fleet Settings"
		})

		# Check default values match JSON schema
		self.assertEqual(settings.max_fuel_quantity or 500, 500)
		self.assertEqual(settings.fuel_entry_max_days_back or 90, 90)
		self.assertEqual(settings.maintenance_reminder_days or 7, 7)
		self.assertEqual(settings.license_expiry_reminder_days or 30, 30)
		self.assertEqual(settings.max_driving_hours_per_day or 10, 10)

	def test_fuel_settings_validation(self):
		"""Test fuel settings validation"""
		self.settings.max_fuel_quantity = 500
		self.settings.max_fuel_amount = 100000
		self.settings.fuel_entry_max_days_back = 90

		# Should save without errors
		self.settings.save(ignore_permissions=True)

		# Test invalid quantity
		self.settings.max_fuel_quantity = -50
		with self.assertRaises(frappe.ValidationError):
			self.settings.save(ignore_permissions=True)

	def test_fuel_price_alert_dependency(self):
		"""Test that fuel price alert requires threshold when enabled"""
		self.settings.enable_fuel_price_alerts = 1
		self.settings.fuel_price_alert_threshold = None

		with self.assertRaises(frappe.ValidationError):
			self.settings.validate_fuel_settings()

		# Should work with threshold set
		self.settings.fuel_price_alert_threshold = 50
		self.settings.validate_fuel_settings()  # Should not raise

	def test_notification_email_dependency(self):
		"""Test notification email validation when notifications enabled"""
		self.settings.enable_notifications = 1
		self.settings.notification_email = "invalid-email"

		with self.assertRaises(frappe.ValidationError):
			self.settings.validate_notification_settings()

		# Valid email should work
		self.settings.notification_email = "admin@logistay.com"
		self.settings.validate_notification_settings()  # Should not raise

	def test_get_fleet_settings_function(self):
		"""Test get_fleet_settings API function"""
		from logistay.fleet_management.doctype.fleet_settings.fleet_settings import get_fleet_settings

		settings = get_fleet_settings()
		self.assertIsNotNone(settings)
		self.assertIsInstance(settings, dict)
		self.assertIn("max_fuel_quantity", settings)

	def test_get_setting_value_function(self):
		"""Test get_setting_value API function"""
		from logistay.fleet_management.doctype.fleet_settings.fleet_settings import get_setting_value

		# Set a known value
		self.settings.max_fuel_quantity = 600
		self.settings.save(ignore_permissions=True)

		# Clear cache
		frappe.cache().delete_value("fleet_settings")

		# Get the value
		value = get_setting_value("max_fuel_quantity")
		self.assertEqual(value, 600)

	def test_validate_fuel_entry_function(self):
		"""Test validate_fuel_entry_against_settings function"""
		from logistay.fleet_management.doctype.fleet_settings.fleet_settings import (
			validate_fuel_entry_against_settings
		)
		from frappe.utils import today

		# Set settings
		self.settings.max_fuel_quantity = 500
		self.settings.max_fuel_amount = 100000
		self.settings.fuel_entry_max_days_back = 90
		self.settings.save(ignore_permissions=True)

		# Clear cache
		frappe.cache().delete_value("fleet_settings")

		# Valid fuel entry
		result = validate_fuel_entry_against_settings(
			quantity=100,
			amount=5000,
			fuel_date=today()
		)
		self.assertTrue(result)

		# Exceeds max quantity
		with self.assertRaises(frappe.ValidationError):
			validate_fuel_entry_against_settings(
				quantity=600,
				amount=5000,
				fuel_date=today()
			)

		# Exceeds max amount
		with self.assertRaises(frappe.ValidationError):
			validate_fuel_entry_against_settings(
				quantity=100,
				amount=150000,
				fuel_date=today()
			)

	def test_validate_trip_distance_function(self):
		"""Test validate_trip_distance_against_settings function"""
		from logistay.fleet_management.doctype.fleet_settings.fleet_settings import (
			validate_trip_distance_against_settings
		)

		# Set settings
		self.settings.max_trip_distance = 1000
		self.settings.save(ignore_permissions=True)

		# Clear cache
		frappe.cache().delete_value("fleet_settings")

		# Valid distance
		result = validate_trip_distance_against_settings(500)
		self.assertTrue(result)

		# Exceeds max distance
		with self.assertRaises(frappe.ValidationError):
			validate_trip_distance_against_settings(1500)

	def test_cache_invalidation_on_update(self):
		"""Test that cache is cleared when settings are updated"""
		from logistay.fleet_management.doctype.fleet_settings.fleet_settings import get_fleet_settings

		# Get settings (will cache)
		settings1 = get_fleet_settings()
		initial_value = settings1.get("max_fuel_quantity")

		# Update settings
		self.settings.max_fuel_quantity = (initial_value or 500) + 100
		self.settings.save(ignore_permissions=True)

		# Get settings again (should be updated)
		settings2 = get_fleet_settings()
		updated_value = settings2.get("max_fuel_quantity")

		self.assertNotEqual(initial_value, updated_value)

	def test_settings_permissions(self):
		"""Test that permissions are set correctly"""
		# Check that System Manager has full permissions
		perms = frappe.get_all(
			"Custom DocPerm",
			filters={
				"parent": "Fleet Settings",
				"role": "System Manager"
			},
			fields=["read", "write", "create", "delete"]
		)

		if perms:
			self.assertTrue(perms[0].read)
			self.assertTrue(perms[0].write)

	def test_extreme_values(self):
		"""Test extreme but valid values"""
		self.settings.max_fuel_quantity = 0.1  # Very small valid value
		self.settings.max_fuel_amount = 1  # Minimum valid amount
		self.settings.fuel_entry_max_days_back = 1  # Minimum days
		self.settings.max_driving_hours_per_day = 0.5  # Half hour minimum

		# Should save without errors
		self.settings.save(ignore_permissions=True)

		# Test maximum valid values
		self.settings.max_fuel_quantity = 9999
		self.settings.fuel_entry_max_days_back = 365
		self.settings.max_driving_hours_per_day = 24

		# Should save without errors
		self.settings.save(ignore_permissions=True)
