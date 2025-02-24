// Copyright (c) 2025, Ketan Patel and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Property Contribution Summary", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Property Contribution Summary', {
    property: function(frm) {
        if (frm.doc.property) {
            frappe.call({
                method: 'property_management.property_management.doctype.property_contribution_summary.property_contribution_summary.get_property_contribution_details',
                args: {
                    property_name: frm.doc.property
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('total_expense', r.message.total_expense);
                        frm.set_value('actual_contribution', r.message.actual_contribution);
                        frm.set_value('total_contribution', r.message.total_contribution);

                        // Clear and populate the shareholder contribution table
                        frm.clear_table('shareholder_contribution');
                        $.each(r.message.shareholder_contribution, function(_i, d) {
                            let row = frm.add_child('shareholder_contribution');
                            Object.keys(d).forEach(field => {
                                row[field] = d[field]; // Set all fields dynamically
                            });
                            row.__unsaved = 1;
                        });
                        frm.refresh_field('shareholder_contribution');
                        frm.dirty();
                        frm.save()
                    }
                }
            });
        }
    }
});
