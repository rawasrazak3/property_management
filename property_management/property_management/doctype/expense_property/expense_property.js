// Copyright (c) 2024, Ketan Patel and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Expense Property", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Expense Property', {
    refresh: function(frm) {
        frm.set_query('property', function() {
            return {
                filters: {
                    custom_property_type: 'Land'
                }
            };
        });
    }
});

frappe.ui.form.on('Expense Property', {
    property: function(frm) {
        if (frm.doc.property) {
            // Fetch assets where custom_against_property matches the selected property
            frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    doctype: 'Asset',
                    filters: {
                        split_from: frm.doc.property  // Match against the selected property ID
                    },
                    fields: ['name', 'gfa_sqft', 'gross_purchase_amount']  // Fields to fetch
                },
                callback: function(r) {
                    // Clear existing rows in the child table
                    frm.clear_table('land_property');

                    // Add fetched assets to the child table, if any
                    if (r.message && r.message.length > 0) {
                        r.message.forEach(asset => {
                            let child = frm.add_child('land_property');
                            child.property = asset.name;
                            child.gfa_sqft = asset.gfa_sqft;
                            child.gross_amount = asset.gross_purchase_amount;
                        });
                    }

                    // Fetch the selected asset's details and add it to the child table
                    frappe.call({
                        method: 'frappe.client.get',
                        args: {
                            doctype: 'Asset',
                            name: frm.doc.property  // Fetch the selected property asset details
                        },
                        callback: function(r) {
                            if (r && r.message) {
                                let asset = r.message;

                                // Add the selected asset to the child table
                                let child = frm.add_child('land_property');
                                child.property = asset.name;
                                child.gfa_sqft = asset.gfa_sqft;
                                child.gross_amount = asset.gross_purchase_amount;

                                // Refresh the child table to show the changes
                                frm.refresh_field('land_property');
                            }
                        }
                    });
                }
            });
        }
    }
});

frappe.ui.form.on('Expense Property', {
    onload: function(frm) {
        calculate_total_expense(frm);
    },
    refresh: function(frm) {
        calculate_total_expense(frm);
    },
    'expense_account_on_form_rendered': function(frm) {
        calculate_total_expense(frm);
    },
    'expense_account_remove': function(frm) {
        calculate_total_expense(frm);
    },
});

function calculate_total_expense(frm) {
    let total = 0;

    // Loop through the child table to calculate total amount
    frm.doc.expense_account.forEach(function(expense) {
        total += expense.amount || 0; // Add amount, default to 0 if undefined
    });

    // Set the total in the main doctype
    frm.set_value('total_expense_amount', total);
}

frappe.ui.form.on('Expense Property', {
    before_save: function(frm) {
        let total_expense_amount = frm.doc.total_expense_amount;
        let row_count = frm.doc.land_property.length;

        if (row_count > 0) {
            let split_amount = total_expense_amount / row_count;

            frm.doc.land_property.forEach(function(row) {
                if (!row.allocated_expense_amount) {
                    row.allocated_expense_amount = split_amount;
                }
            });
        }
        frm.refresh_field('land_property');
    }
});

frappe.ui.form.on('Expense Property', {
    before_submit: function(frm) {
        let total_allocated_expense = 0;
        frm.doc.land_property.forEach(function(row) {
            total_allocated_expense += row.allocated_expense_amount;
        });

        if (total_allocated_expense !== frm.doc.total_expense_amount) {
            frappe.throw(__('Total Allocated Expense Amount must be equal to Total Expense Amount'));
        }
    }
});

  
// frappe.ui.form.on('Expense Property', {
//     refresh: function(frm) {
//         frm.add_custom_button(__('Create Journal Entry'), function() {
//             prepare_journal_entry_data(frm);
//         });
//     }
// });

// function prepare_journal_entry_data(frm) {
//     let journal_entries = {};
//     let promises = [];

//     // Loop through each asset in the land_property child table
//     frm.doc.land_property.forEach(function(asset_row) {
//         promises.push(frappe.call({
//             method: 'frappe.client.get',
//             args: {
//                 doctype: 'Asset',
//                 name: asset_row.property
//             },
//             callback: function(asset_data) {
//                 let allocated_expense = asset_row.allocated_expense_amount;

//                 // Fetch shareholders and accounts directly from Shareholder Property table
//                 asset_data.message.custom_shareholder_table.forEach(function(shareholder_row) {
//                     let shareholder = shareholder_row.shareholder;
//                     let shareholder_account = shareholder_row.shareholder_account;
//                     let contribution_percent = shareholder_row.contribution;

//                     // Calculate allocation based on contribution percentage
//                     let allocation_amount = (allocated_expense * (contribution_percent / 100));

//                     if (!journal_entries[shareholder]) {
//                         journal_entries[shareholder] = {
//                             account: shareholder_account,
//                             party_type: 'Shareholder',
//                             party: shareholder,
//                             credit_in_account_currency: 0
//                         };
//                     }
//                     journal_entries[shareholder].credit_in_account_currency += allocation_amount;
//                 });
//             }
//         }));
//     });

//     Promise.all(promises).then(() => {
//         // Prepare data for Journal Entry form
//         let accounts = Object.values(journal_entries).map(entry => ({
//             account: entry.account,
//             party_type: entry.party_type,
//             party: entry.party,
//             credit_in_account_currency: entry.credit_in_account_currency
//         }));

//         // Redirect to the new Journal Entry form with pre-filled data
//         frappe.new_doc('Journal Entry', {
//             posting_date: frappe.datetime.nowdate(),
//             accounts: accounts
//         });
//     });
// }

frappe.ui.form.on('Expense Property', {
    refresh: function(frm) {
        frm.add_custom_button(__('Create Journal Entry'), function() {
            show_mode_of_payment_dialog(frm);
        });
    }
});

function show_mode_of_payment_dialog(frm) {
    // Create a dialog box for selecting mode of payment
    let dialog = new frappe.ui.Dialog({
        title: __('Select Mode of Payment'),
        fields: [
            {
                label: 'Mode of Payment',
                fieldname: 'mode_of_payment',
                fieldtype: 'Link',
                options: 'Mode of Payment',
                reqd: 1
            }
        ],
        primary_action_label: __('Continue'),
        primary_action(values) {
            dialog.hide();
            frappe.call({
                method: "property_management.property_management.doctype.expense_property.expense_property.create_journal_entry_with_mode_of_payment",
                args: {
                    expense_property: frm.doc.name,
                    mode_of_payment: values.mode_of_payment
                },
                callback: function(response) {
                    if (response.message) {
                        // Create a new Journal Entry form with pre-filled data
                        frappe.new_doc("Journal Entry");
                        frappe.ui.form.on("Journal Entry", "onload", function(je_frm) {
                            // Set posting date
                            frappe.model.set_value(je_frm.doctype, je_frm.docname, "posting_date", response.message.posting_date);

                            // Set custom_is_expense_property to true for Expense Property related entries
                            frappe.model.set_value(je_frm.doctype, je_frm.docname, "custom_is_expense_property", 1);

                            // Clear the accounts table and populate with data
                            je_frm.clear_table("accounts");
                            response.message.accounts.forEach(account => {
                                let row = frappe.model.add_child(je_frm.doc, "accounts");
                                frappe.model.set_value(row.doctype, row.name, "account", account.account);
                                frappe.model.set_value(row.doctype, row.name, "party_type", "Shareholder");
                                frappe.model.set_value(row.doctype, row.name, "party", account.party);
                                frappe.model.set_value(row.doctype, row.name, "credit_in_account_currency", account.credit_in_account_currency);
                                frappe.model.set_value(row.doctype, row.name, "debit_in_account_currency", account.debit_in_account_currency);

                                // Set reference_type as "Property" and reference_name as the specific property (asset) name
                                frappe.model.set_value(row.doctype, row.name, "reference_type", "Asset");
                                frappe.model.set_value(row.doctype, row.name, "reference_name", account.reference_name);
                                frappe.model.set_value(row.doctype, row.name, "party_type", "Shareholder");
                            });

                            // Refresh the child table to ensure it's editable
                            je_frm.refresh_field("accounts");
                        });
                    }
                }
            });
        }
    });
    dialog.show();
}




// function show_mode_of_payment_dialog(frm) {
//     // Create a dialog box for selecting mode of payment
//     let dialog = new frappe.ui.Dialog({
//         title: __('Select Mode of Payment'),
//         fields: [
//             {
//                 label: 'Mode of Payment',
//                 fieldname: 'mode_of_payment',
//                 fieldtype: 'Link',
//                 options: 'Mode of Payment',
//                 reqd: 1
//             }
//         ],
//         primary_action_label: __('Continue'),
//         primary_action(values) {
//             dialog.hide();
//             frappe.call({
//                 method: "property_management.property_management.doctype.expense_property.expense_property.create_journal_entry_with_mode_of_payment",
//                 args: {
//                     expense_property: frm.doc.name,
//                     mode_of_payment: values.mode_of_payment
//                 },
//                 callback: function(response) {
//                     if (response.message) {
//                         frappe.set_route("Form", "Journal Entry", response.message);  // Redirect to the Journal Entry
//                     }
//                 }
//             });
//         }
//     });
//     dialog.show();
// }
