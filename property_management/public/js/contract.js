frappe.ui.form.on('Contract', {
    refresh: function(frm) {
        // Add the custom action button under the "Actions" dropdown
        frm.add_custom_button(__('Create Maintenance Service Charge'), function() {
            frappe.new_doc('Maintenance Service Charge', {
                customer: frm.doc.name, 
                contract_id: frm.doc.name 

            });
        }, __('Action')); 
    }
});
