// Copyright (c) 2025, Ketan Patel and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Shareholder Exit", {
// 	refresh(frm) {

// 	},
// });
//amount in gross amount
frappe.ui.form.on('Shareholder Exit', {
    property: function(frm) {
        // Clear shareholder and share amount when property is changed
        frm.set_value('shareholder', null);
        frm.set_value('share_amount', 0);
        frm.set_value('amount', 0); // Clear amount as well

        if (frm.doc.property) {
            // Fetch Property Shareholder document
            frappe.db.get_value('Property Shareholder', { property: frm.doc.property }, 'name')
                .then(res => {
                    if (res.message) {
                        const docname = res.message.name;

                        // Fetch the full Property Shareholder document
                        frappe.db.get_doc('Property Shareholder', docname)
                            .then(doc => {
                                // ✅ Set child table cache for filtering
                                frm.property_shareholders = doc.shareholder || [];

                                // ✅ Set amount from gross_purchase_amount
                                frm.set_value('amount', doc.gross_purchase_amount || 0);
                            });
                    }
                });
        }
    },

    refresh: function(frm) {
        frm.set_query('shareholder', function() {
            if (frm.property_shareholders) {
                return {
                    filters: [['name', 'in', frm.property_shareholders.map(d => d.shareholder)]]
                };
            }
        });
    },

    shareholder: function(frm) {
        if (frm.doc.shareholder && frm.property_shareholders) {
            let selected = frm.property_shareholders.find(d => d.shareholder === frm.doc.shareholder);
            frm.set_value('share_amount', selected ? selected.amount : 0);
        }
    }
});
//-------------------------------------------------------------------------------------

// frappe.ui.form.on('Shareholder Exit', {
//     property: function(frm) {
//         // Clear shareholder and share amount when property is changed
//         frm.set_value('shareholder', null);
//         frm.set_value('share_amount', 0);

//         if (frm.doc.property) {
//             // Fetch Property Shareholder document to get the child table data
//             frappe.db.get_value('Property Shareholder', { property: frm.doc.property }, 'name')
//                 .then(res => {
//                     if (res.message) {
//                         frappe.db.get_doc('Property Shareholder', res.message.name)
//                             .then(doc => {
//                                 // Store all shareholder details in an array for filtering
//                                 frm.property_shareholders = doc.shareholder || [];
//                             });
//                     }
//                 });
//         }
//     },

//     refresh: function(frm) {
//         // Filter the shareholder options based on the selected property
//         frm.set_query('shareholder', function() {
//             if (frm.property_shareholders) {
//                 return {
//                     filters: [['name', 'in', frm.property_shareholders.map(d => d.shareholder)]]
//                 };
//             }
//         });
//     },

//     shareholder: function(frm) {
//         // Fetch share amount when a shareholder is selected
//         if (frm.doc.shareholder && frm.property_shareholders) {
//             let selected = frm.property_shareholders.find(d => d.shareholder === frm.doc.shareholder);
//             frm.set_value('share_amount', selected ? selected.amount : 0);
//         }
//     }
// });
frappe.ui.form.on('Shareholder Exit', {
    shareholder: function(frm) {
        if (frm.doc.property && frm.doc.shareholder) {
            frappe.call({
                method: "property_management.property_management.doctype.shareholder_exit.shareholder_exit.get_existing_shareholder_exit",
                args: {
                    property: frm.doc.property,
                    shareholder: frm.doc.shareholder
                },
                
            });
        }
    },
    // // Optionally, you can also run this check on form load
    // onload: function(frm) {
    //     if (frm.doc.property && frm.doc.shareholder) {
    //         frappe.call({
    //             method: "property_management.property_management.doctype.shareholder_exit.shareholder_exit.get_existing_shareholder_exit",
    //             args: {
    //                 property: frm.doc.property,
    //                 shareholder: frm.doc.shareholder
    //             },
    //             callback: function(r) {
    //                 if (r.message) {
    //                     // Redirect to existing Shareholder Exit document if found
    //                     frappe.set_route("Form", "Shareholder Exit", r.message);
    //                 }
    //             }
    //         });
    //     }
    // }
});
frappe.ui.form.on("Shareholder Exit", {
    create_journal: function(frm) {
        const required_fields = [
            'shareholder',
            'shareholder_account',
            'mode_of_payment',
            'exit_amount',
            'company',
            'exit_date'
        ];

        const missing = required_fields.filter(field => !frm.doc[field]);
        if (missing.length > 0) {
            frappe.msgprint(__('Please fill all required fields: {0}', [missing.join(', ')]));
            return;
        }
        // ✅ 1. Exit amount validation against outstanding amount
        let outstandingAmount = 0;
        if (frm.doc.partial_payments && frm.doc.partial_payments.length > 0) {
            const lastRow = frm.doc.partial_payments[frm.doc.partial_payments.length - 1];
            outstandingAmount = parseFloat(lastRow.outstanding_amount || 0);
        } else {
            outstandingAmount = parseFloat(frm.doc.share_amount || 0);
        }
        const exitAmount = parseFloat(frm.doc.exit_amount || 0);
        if (exitAmount > outstandingAmount) {
            frappe.msgprint(`Please Enter Less Than Outstanding Amount ₹${outstanding_amount}`);
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
                exit_date: frm.doc.exit_date,
                project: frm.doc.project,
                shareholder_account: frm.doc.shareholder_account
            },
            freeze: true,
            freeze_message: "Creating Journal Entry...",
            callback: function(response) {
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

                    frappe.db.set_value("Journal Entry", journal_entry_name, "custom_is_shareholder_exit", 1)
                        .then(() => {
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

// frappe.ui.form.on("Shareholder Exit", {
//     transfer_to_main: function(frm) {
//         const required_fields = ['property', 'mode_of_payment2', 'exit_amount', 'company', 'transfer_date'];
//         const missing = required_fields.filter(field => !frm.doc[field]);

//         if (missing.length > 0) {
//             frappe.msgprint(__('Please fill all required fields: {0}', [missing.join(', ')]));
//             return;
//         }

//         // ✅ Get Outstanding from second-last row or share_amount
//         let outstanding_amount = 0.0;
//         const len = frm.doc.partial_payments ? frm.doc.partial_payments.length : 0;
//         if (len >= 2) {
//             outstanding_amount = parseFloat(frm.doc.partial_payments[len - 2].outstanding_amount || 0);
//         } else {
//             outstanding_amount = parseFloat(frm.doc.share_amount || 0);
//         }

//         if (parseFloat(frm.doc.exit_amount) > outstanding_amount) {
//             frappe.msgprint(`Please Enter Less Than Outstanding Amount ₹${outstanding_amount}`);
//             return;
//         }

//         frappe.call({
//             method: "property_management.property_management.doctype.shareholder_exit.shareholder_exit.create_transfer_journal_entry",
//             args: {
//                 asset: frm.doc.property,
//                 mode_of_payment2: frm.doc.mode_of_payment2,
//                 exit_amount: frm.doc.exit_amount,
//                 company: frm.doc.company,
//                 date: frm.doc.transfer_date, // ✅ use transfer_date for posting_date
//                 project: frm.doc.project
//             },
//             freeze: true,
//             freeze_message: "Creating Journal Entry...",
//             callback: function(response) {
//                 if (response.message) {
//                     // ✅ Add to transfer_table
//                     const row = frm.add_child("transfer_table");
//                     row.transfer_journal = response.message;
//                     row.transfer_amount = frm.doc.exit_amount;

//                     frm.refresh_field("transfer_table");

//                     frm.save().then(() => {
//                         frappe.set_route("Form", "Journal Entry", response.message);
//                     });
//                 } else {
//                     frappe.msgprint(__('Failed to create Journal Entry. No name returned.'));
//                 }
//             }
//             on_submit: function(frm) {
//                 frappe.call({
//                     method: "property_management.property_management.doctype.shareholder_exit.shareholder_exit.update_property_shareholder_child_table",
//                     args: {
//                         shareholder_exit_name: frm.doc.name
//                     },
//                     freeze: true,
//                     freeze_message: "Updating Property Shareholder...",
//                     callback: function(response) {
//                         if (response.message) {
//                             frappe.msgprint(__('Property Shareholder updated successfully.'));
//                         } else {
//                             frappe.msgprint(__('Failed to update Property Shareholder.'));
//                         }
//                     }
//                 });
//             }
//         });
//     },
// });

frappe.ui.form.on("Shareholder Exit", {
    transfer_to_main: function(frm) {
        const required_fields = ['property', 'mode_of_payment2', 'exit_amount', 'company', 'transfer_date'];
        const missing = required_fields.filter(field => !frm.doc[field]);

        if (missing.length > 0) {
            frappe.msgprint(__('Please fill all required fields: {0}', [missing.join(', ')]));
            return;
        }
        // ✅ Get Outstanding from second-last row or share_amount
        let outstanding_amount = 0.0;
        const len = frm.doc.partial_payments ? frm.doc.partial_payments.length : 0;
        if (len >= 2) {
            outstanding_amount = parseFloat(frm.doc.partial_payments[len - 2].outstanding_amount || 0);
        } else {
            outstanding_amount = parseFloat(frm.doc.share_amount || 0);
        }
        if (parseFloat(frm.doc.exit_amount) > outstanding_amount) {
            frappe.msgprint(`Please Enter Less Than Outstanding Amount ₹${outstanding_amount}`);
            return;
        }
        frappe.call({
            method: "property_management.property_management.doctype.shareholder_exit.shareholder_exit.create_transfer_journal_entry",
            args: {
                asset: frm.doc.property,
                mode_of_payment2: frm.doc.mode_of_payment2,
                exit_amount: frm.doc.exit_amount,
                company: frm.doc.company,
                date: frm.doc.transfer_date,  // ✅ use transfer_date for posting_date
                project: frm.doc.project
            },
            freeze: true,
            freeze_message: "Creating Journal Entry...",
            callback: function(response) {
                if (response.message) {
                    // ✅ Add to transfer_table
                    const row = frm.add_child("transfer_table");
                    row.transfer_journal = response.message;
                    row.transfer_amount = frm.doc.exit_amount;

                    frm.refresh_field("transfer_table");

                    frm.save().then(() => {
                        frappe.set_route("Form", "Journal Entry", response.message);
                    });
                } else {
                    frappe.msgprint(__('Failed to create Journal Entry. No name returned.'));
                }
            }
        });
    }
});
// update property shareholder doc

frappe.ui.form.on("Shareholder Exit", {
    transfer_to_main: function(frm) {
        frappe.call({
            method: "property_management.property_management.doctype.shareholder_exit.shareholder_exit.update_property_shareholder_child_table",
            args: {
                shareholder_exit_name: frm.doc.name
            },
            freeze: true,
            freeze_message: "Updating Property Shareholder...",
            callback: function(response) {
                frm.save();
            }
        });
    }
});

//validation
// frappe.ui.form.on('Shareholder Exit', {
//     validate: function (frm) {
//         var partial_payments_count = frm.doc.partial_payments ? frm.doc.partial_payments.length : 0;
//         var transfer_table_count = frm.doc.transfer_table ? frm.doc.transfer_table.length : 0;

//         // Check if row counts are equal before submission
//         if (partial_payments_count !== transfer_table_count) {
//             frappe.msgprint(__("Number of rows in Partial Payments ({0}) must be equal to Transfer Table ({1}).", 
//                               [partial_payments_count, transfer_table_count]));
//             frappe.validated = false; // Prevent form submission
//         }
//     }
// });
frappe.ui.form.on('Shareholder Exit', {
    refresh: function(frm) {
        // Hide the field initially
        frm.toggle_display('outstanding_amount', false);

        // Show and update only if shareholder is selected
        if (frm.doc.shareholder) {
            show_outstanding_amount(frm);
        }
    },

    shareholder: function(frm) {
        if (frm.doc.shareholder) {
            show_outstanding_amount(frm);
        } else {
            frm.toggle_display('outstanding_amount', false);
        }
    }
});

function show_outstanding_amount(frm) {
    if (frm.doc.partial_payments && frm.doc.partial_payments.length > 0) {
        const lastRow = frm.doc.partial_payments[frm.doc.partial_payments.length - 1];
        const outstandingAmount = parseFloat(lastRow.outstanding_amount || 0);

        const html = `<div style="color: white; font-weight: bold; padding: 8px; border-radius: 6px;">
            Outstanding Amount: ₹ ${outstandingAmount.toFixed(2)}
        </div>`;

        frm.set_df_property('outstanding_amount', 'options', html);
        frm.toggle_display('outstanding_amount', true);
        frm.refresh_field('outstanding_amount');
    }
}