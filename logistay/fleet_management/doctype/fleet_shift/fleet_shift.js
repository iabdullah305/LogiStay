// Copyright (c) 2023, Your Company and contributors
// For license information, please see license.txt

frappe.ui.form.on('Fleet Shift', {
    refresh: function(frm) {
        // Add custom buttons
        if (frm.doc.docstatus === 1 && frm.doc.status === "SCHEDULED") {
            frm.add_custom_button(__('Mark as Completed'), function() {
                frappe.confirm(
                    __('Are you sure you want to mark this shift as completed?'),
                    function() {
                        frm.set_value('status', 'COMPLETED');
                        frm.save();
                    }
                );
            });
        }
        
        // Add button to view driver schedule
        frm.add_custom_button(__('View Driver Schedule'), function() {
            frappe.route_options = {
                "fleet_driver": frm.doc.fleet_driver,
                "from_date": frappe.datetime.add_days(frm.doc.shift_date, -7),
                "to_date": frappe.datetime.add_days(frm.doc.shift_date, 7)
            };
            frappe.set_route("List", "Fleet Shift", "Calendar");
        }, __("View"));
        
        // Add button to view vehicle schedule
        frm.add_custom_button(__('View Vehicle Schedule'), function() {
            frappe.route_options = {
                "fleet_vehicle": frm.doc.fleet_vehicle,
                "from_date": frappe.datetime.add_days(frm.doc.shift_date, -7),
                "to_date": frappe.datetime.add_days(frm.doc.shift_date, 7)
            };
            frappe.set_route("List", "Fleet Shift", "Calendar");
        }, __("View"));
    },
    
    fleet_project: function(frm) {
        // Clear branch when project changes
        frm.set_value('fleet_branch', '');
    }
});