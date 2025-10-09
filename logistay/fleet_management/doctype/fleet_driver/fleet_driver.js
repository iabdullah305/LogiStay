frappe.ui.form.on('Fleet Driver', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('Assign Vehicle'), function() {
                frappe.new_doc('Driver Vehicle Assignment', {
                    driver: frm.doc.name
                });
            }, __('Create'));
        }
    }
});