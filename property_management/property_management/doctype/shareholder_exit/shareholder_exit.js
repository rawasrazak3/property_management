// Copyright (c) 2025, Ketan Patel and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Shareholder Exit", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Shareholder Exit', {
    property: function(frm) {
        // Clear shareholder and share amount when property is changed
        frm.set_value('shareholder', null);
        frm.set_value('share_amount', 0);

        if (frm.doc.property) {
            // Fetch Property Shareholder document to get the child table data
            frappe.db.get_value('Property Shareholder', { property: frm.doc.property }, 'name')
                .then(res => {
                    if (res.message) {
                        frappe.db.get_doc('Property Shareholder', res.message.name)
                            .then(doc => {
                                // Store all shareholder details in an array for filtering
                                frm.property_shareholders = doc.shareholder || [];
                            });
                    }
                });
        }
    },

    refresh: function(frm) {
        // Filter the shareholder options based on the selected property
        frm.set_query('shareholder', function() {
            if (frm.property_shareholders) {
                return {
                    filters: [['name', 'in', frm.property_shareholders.map(d => d.shareholder)]]
                };
            }
        });
    },

    shareholder: function(frm) {
        // Fetch share amount when a shareholder is selected
        if (frm.doc.shareholder && frm.property_shareholders) {
            let selected = frm.property_shareholders.find(d => d.shareholder === frm.doc.shareholder);
            frm.set_value('share_amount', selected ? selected.amount : 0);
        }
    }
});
frappe.ui.form.on("Shareholder Exit", {
    create_journal: function(frm) {
        const required_fields = [
            'shareholder',
            'shareholder_account',
            'mode_of_payment',
            'exit_amount',
            'company'
        ];

        const missing = required_fields.filter(field => !frm.doc[field]);
        if (missing.length > 0) {
            frappe.msgprint(__('Please fill all required fields: {0}', [missing.join(', ')]));
            return;
        }

        frappe.call({
            method: "property_management.property_management.doctype.shareholder_exit.shareholder_exit.create_shareholder_exit_journal_entry",
            args: {
                asset: frm.doc.property,
                shareholder: frm.doc.shareholder,
                mode_of_payment: frm.doc.mode_of_payment,
                contribution: frm.doc.exit_amount,
                exit_amount: frm.doc.exit_amount,
                company: frm.doc.company,
                date: frm.doc.posting_date || frappe.datetime.get_today(),
                project: frm.doc.project,
                shareholder_account: frm.doc.shareholder_account
            },
            freeze: true,
            freeze_message: "Creating Journal Entry...",
            callback: function(response) {
                console.log("Journal Entry response:", response);
            
                let journal_entry_name = response.message || response.journal_entry;
            
                if (journal_entry_name) {
                    let current_paid = parseFloat(frm.doc.exit_amount || 0);
                    let total_share_amount = parseFloat(frm.doc.share_amount || 0);
            
                    let total_paid_before = frm.doc.partial_payments.reduce((sum, row) => {
                        return sum + (parseFloat(row.paid_amount) || 0);
                    }, 0);
            
                    const row = frm.add_child("partial_payments");
                    row.journal_entry = journal_entry_name;
                    row.paid_amount = current_paid;
                    row.outstanding_amount = total_share_amount - (total_paid_before + current_paid);
            
                    frm.refresh_field("partial_payments");
            
                    // ✅ Set the checkbox in Journal Entry
                    frappe.db.set_value("Journal Entry", journal_entry_name, "custom_is_shareholder_exit", 1)
                        .then(() => {
                            // frappe.msgprint(`Journal Entry <b>${journal_entry_name}</b> created.`);
                            frm.save().then(() => {
                                frappe.set_route("Form", "Journal Entry", journal_entry_name);
                            });
                        });
                } else {
                    frappe.msgprint(__('Failed to create Journal Entry. Response: ') + JSON.stringify(response));
                }
            }
            
        });
    },

    refresh: function(frm) {
        // Show outstanding amount in HTML field
        const lastRow = frm.doc.partial_payments && frm.doc.partial_payments.length > 0 
                        ? frm.doc.partial_payments[frm.doc.partial_payments.length - 1] 
                        : null;
        
        if (lastRow) {
            const outstandingAmount = lastRow.outstanding_amount;
            const html = `<div style="color: white; font-weight: bold;  padding: 8px; border-radius: 6px;">
                Outstanding Amount: ₹ ${outstandingAmount.toFixed(2)}
            </div>`;
            frm.set_df_property('outstanding_amount', 'options', html);
        }
    }
});
frappe.ui.form.on("Shareholder Exit", {
    shareholder: function(frm) {
        if (frm.doc.shareholder && frm.doc.property) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Shareholder Exit",
                    filters: {
                        shareholder: frm.doc.shareholder,
                        property: frm.doc.property,
                        docstatus: 0,
                        name: ["!=", frm.doc.name]  // Exclude current doc
                    },
                    limit: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const existing_doc = r.message[0];
                        frappe.set_route("Form", "Shareholder Exit", existing_doc.name);
                    }
                }
            });
        }
    }
});


// Transfer to main 
frappe.ui.form.on("Shareholder Exit", {
    transfer_to_main: function(frm) {
        const required_fields = ['property', 'mode_of_payment2', 'exit_amount', 'company'];
        const missing = required_fields.filter(field => !frm.doc[field]);
        
        if (missing.length > 0) {
            frappe.msgprint(__('Please fill all required fields: {0}', [missing.join(', ')]));
            return;
        }

        frappe.call({
            method: "property_management.property_management.doctype.shareholder_exit.shareholder_exit.create_transfer_journal_entry",
            args: {
                asset: frm.doc.property,
                mode_of_payment2: frm.doc.mode_of_payment2,
                exit_amount: frm.doc.exit_amount,
                company: frm.doc.company,
                date: frm.doc.posting_date || frappe.datetime.get_today(),
                project: frm.doc.project
            },
            freeze: true,
            freeze_message: "Creating Journal Entry...",
            callback: function(response) {
                if (response.message) {
                    frappe.set_route("Form", "Journal Entry", response.message);
                } else {
                    frappe.msgprint(__('Failed to create Journal Entry. No name returned.'));
                }
            }
        });
    }
});
//update property shareholder doc

frappe.ui.form.on("Shareholder Exit", {
    transfer_to_main: function(frm) {
        // After creating the journal entry, call the Python function to update Property Shareholder child table
        frappe.call({
            method: "property_management.property_management.doctype.shareholder_exit.shareholder_exit.update_property_shareholder_child_table",
            args: {
                shareholder_exit_name: frm.doc.name
            },
            freeze: true,
            freeze_message: "Updating Property Shareholder...",
            callback: function(response) {
                // frappe.msgprint(__('Property Shareholder child table updated successfully.'));
                frm.save();  // Optionally save the Shareholder Exit document after making changes
            }
        });
    }
});







