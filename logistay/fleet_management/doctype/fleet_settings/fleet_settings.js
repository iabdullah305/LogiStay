// Copyright (c) 2025, AFMCOltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Fleet Settings', {
	/**
	 * Called when the form is refreshed
	 * @param {object} frm - The form object
	 */
	refresh(frm) {
		// Add custom buttons
		frm.add_custom_button(__('Reset to Defaults'), () => {
			reset_to_defaults(frm);
		}, __('Actions'));

		frm.add_custom_button(__('Test Notifications'), () => {
			test_notifications(frm);
		}, __('Actions'));

		// Set form indicator
		frm.set_indicator_formatter('Fleet Settings', (doc) => {
			return 'green';
		});

		// Add help text
		frm.set_intro(__('Configure system-wide settings for fleet management operations'), 'blue');
	},

	/**
	 * Called when max fuel quantity changes
	 * @param {object} frm - The form object
	 */
	max_fuel_quantity(frm) {
		validate_positive_number(frm, 'max_fuel_quantity', 'Maximum Fuel Quantity');
	},

	/**
	 * Called when max fuel amount changes
	 * @param {object} frm - The form object
	 */
	max_fuel_amount(frm) {
		validate_positive_number(frm, 'max_fuel_amount', 'Maximum Fuel Amount');
	},

	/**
	 * Called when fuel entry max days back changes
	 * @param {object} frm - The form object
	 */
	fuel_entry_max_days_back(frm) {
		validate_positive_integer(frm, 'fuel_entry_max_days_back', 'Fuel Entry Max Days Back', 365);
	},

	/**
	 * Called when enable fuel price alerts checkbox changes
	 * @param {object} frm - The form object
	 */
	enable_fuel_price_alerts(frm) {
		// Make threshold field mandatory if alerts are enabled
		frm.set_df_property('fuel_price_alert_threshold', 'reqd', frm.doc.enable_fuel_price_alerts);
		frm.refresh_field('fuel_price_alert_threshold');
	},

	/**
	 * Called when fuel price alert threshold changes
	 * @param {object} frm - The form object
	 */
	fuel_price_alert_threshold(frm) {
		if (frm.doc.enable_fuel_price_alerts) {
			validate_positive_number(frm, 'fuel_price_alert_threshold', 'Fuel Price Alert Threshold');
		}
	},

	/**
	 * Called when max trip distance changes
	 * @param {object} frm - The form object
	 */
	max_trip_distance(frm) {
		validate_positive_number(frm, 'max_trip_distance', 'Maximum Trip Distance');
	},

	/**
	 * Called when maintenance reminder days changes
	 * @param {object} frm - The form object
	 */
	maintenance_reminder_days(frm) {
		validate_positive_integer(frm, 'maintenance_reminder_days', 'Maintenance Reminder Days', 365);
	},

	/**
	 * Called when license expiry reminder days changes
	 * @param {object} frm - The form object
	 */
	license_expiry_reminder_days(frm) {
		validate_positive_integer(frm, 'license_expiry_reminder_days', 'License Expiry Reminder Days', 365);
	},

	/**
	 * Called when max driving hours per day changes
	 * @param {object} frm - The form object
	 */
	max_driving_hours_per_day(frm) {
		validate_positive_number(frm, 'max_driving_hours_per_day', 'Maximum Driving Hours Per Day');

		if (frm.doc.max_driving_hours_per_day > 24) {
			frappe.msgprint({
				title: __('Warning'),
				indicator: 'orange',
				message: __('Maximum driving hours per day cannot exceed 24 hours')
			});
			frm.set_value('max_driving_hours_per_day', 24);
		}
	},

	/**
	 * Called when enable notifications checkbox changes
	 * @param {object} frm - The form object
	 */
	enable_notifications(frm) {
		// Make notification email field mandatory if notifications are enabled
		frm.set_df_property('notification_email', 'reqd', frm.doc.enable_notifications);
		frm.refresh_field('notification_email');
	},

	/**
	 * Called when notification email changes
	 * @param {object} frm - The form object
	 */
	notification_email(frm) {
		if (frm.doc.notification_email) {
			validate_email(frm, 'notification_email');
		}
	}
});

/**
 * Validate that a field contains a positive number
 * @param {object} frm - The form object
 * @param {string} fieldname - Name of the field to validate
 * @param {string} label - Label of the field for error messages
 */
function validate_positive_number(frm, fieldname, label) {
	const value = frm.doc[fieldname];

	if (value !== null && value !== undefined && value <= 0) {
		frappe.msgprint({
			title: __('Validation Error'),
			indicator: 'red',
			message: __('{0} must be greater than zero', [label])
		});
		frm.set_value(fieldname, null);
	}
}

/**
 * Validate that a field contains a positive integer within a max limit
 * @param {object} frm - The form object
 * @param {string} fieldname - Name of the field to validate
 * @param {string} label - Label of the field for error messages
 * @param {number} max_value - Maximum allowed value
 */
function validate_positive_integer(frm, fieldname, label, max_value) {
	const value = frm.doc[fieldname];

	if (value !== null && value !== undefined) {
		if (value < 0) {
			frappe.msgprint({
				title: __('Validation Error'),
				indicator: 'red',
				message: __('{0} cannot be negative', [label])
			});
			frm.set_value(fieldname, 0);
		} else if (value > max_value) {
			frappe.msgprint({
				title: __('Validation Error'),
				indicator: 'red',
				message: __('{0} cannot exceed {1}', [label, max_value])
			});
			frm.set_value(fieldname, max_value);
		}
	}
}

/**
 * Validate email format
 * @param {object} frm - The form object
 * @param {string} fieldname - Name of the email field
 */
function validate_email(frm, fieldname) {
	const email = frm.doc[fieldname];
	const email_regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

	if (email && !email_regex.test(email)) {
		frappe.msgprint({
			title: __('Validation Error'),
			indicator: 'red',
			message: __('Please enter a valid email address')
		});
		frm.set_value(fieldname, '');
	}
}

/**
 * Reset all settings to default values
 * @param {object} frm - The form object
 */
function reset_to_defaults(frm) {
	frappe.confirm(
		__('Are you sure you want to reset all settings to default values? This action cannot be undone.'),
		() => {
			// Reset fuel settings
			frm.set_value('max_fuel_quantity', 500);
			frm.set_value('max_fuel_amount', 100000);
			frm.set_value('fuel_entry_max_days_back', 90);
			frm.set_value('enable_fuel_price_alerts', 0);
			frm.set_value('fuel_price_alert_threshold', null);

			// Reset trip settings
			frm.set_value('max_trip_distance', 1000);
			frm.set_value('enable_trip_approval', 0);
			frm.set_value('default_trip_status', 'Assigned');

			// Reset maintenance settings
			frm.set_value('maintenance_reminder_days', 7);
			frm.set_value('enable_maintenance_alerts', 1);
			frm.set_value('default_maintenance_type', 'Preventive');

			// Reset driver settings
			frm.set_value('license_expiry_reminder_days', 30);
			frm.set_value('enable_driver_performance_tracking', 1);
			frm.set_value('max_driving_hours_per_day', 10);

			// Reset system settings
			frm.set_value('enable_gps_tracking', 0);
			frm.set_value('enable_mobile_app', 1);
			frm.set_value('enable_notifications', 1);
			frm.set_value('notification_email', '');

			frappe.show_alert({
				message: __('Settings have been reset to default values'),
				indicator: 'green'
			}, 5);

			// Save the form
			frm.save();
		}
	);
}

/**
 * Test notification system
 * @param {object} frm - The form object
 */
function test_notifications(frm) {
	if (!frm.doc.enable_notifications) {
		frappe.msgprint({
			title: __('Notifications Disabled'),
			indicator: 'orange',
			message: __('Please enable notifications first')
		});
		return;
	}

	if (!frm.doc.notification_email) {
		frappe.msgprint({
			title: __('Email Required'),
			indicator: 'red',
			message: __('Please set a notification email address')
		});
		return;
	}

	frappe.call({
		method: 'frappe.core.doctype.communication.email.make',
		args: {
			recipients: frm.doc.notification_email,
			subject: __('Test Notification - LogiStay Fleet Management'),
			content: __('This is a test notification from LogiStay Fleet Management System. If you received this email, notifications are working correctly.'),
			send_email: 1
		},
		callback: (r) => {
			if (!r.exc) {
				frappe.show_alert({
					message: __('Test notification sent successfully'),
					indicator: 'green'
				}, 5);
			}
		}
	});
}
