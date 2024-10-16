// Copyright (c) 2024, Ketan Patel and contributors
// For license information, please see license.txt

frappe.ui.form.on("Maintenance Service Charge", {
    refresh: function(frm) {
        // Add the custom action button under the "Actions" dropdown
        frm.add_custom_button(__('Create Payment Entry'), function() {
            frappe.new_doc('Payment Entry', {
                party_type: 'Customer'
                // party_name: frm.doc.name 
            });
        }, __('Action')); 
    }
});
