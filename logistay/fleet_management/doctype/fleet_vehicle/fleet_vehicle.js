frappe.ui.form.on('Fleet Vehicle', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('New Fuel Entry'), function() {
                frappe.new_doc('Fuel Entry', {
                    vehicle: frm.doc.name
                });
            }, __('Create'));
        }
    }
});