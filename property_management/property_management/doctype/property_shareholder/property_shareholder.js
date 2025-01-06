// Copyright (c) 2025, Ketan Patel and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Property Shareholder", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Property Shareholder', {
    refresh: function(frm) {
        calculate_shareholder_amounts(frm);
    },
    // gross_purchase_amount: function(frm) {
    //     calculate_shareholder_amounts(frm);
    // },
    update_before_submit: function(frm) {
        validate_total_contribution(frm);
    },
    before_submit: function(frm) {
        validate_total_contribution(frm);
    },
    property: function(frm) {
        // Ensure the fields have valid numeric values
        let gross_amount = frm.doc.gross_purchase_amount || 0;
        let expense = frm.doc.total_expenses || 0;
    
        // Calculate the updated gross purchase amount
        let updated_amount = gross_amount + expense;
    
        // Set the calculated value back to the field
        frm.set_value('gross_purchase_amount', updated_amount);
    }
    
});

frappe.ui.form.on('Shareholder Property', {
    contribution: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        calculate_row_amount(frm, row);
        frm.refresh_field("shareholder");
        validate_total_contribution(frm);  // Validate after updating a row
    },
    amount: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        calculate_row_contribution(frm, row);
        frm.refresh_field("shareholder");
        validate_total_contribution(frm);  // Validate after updating a row
    },
    onload: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let expense = frm.doc.total_expenses;
        let actual_property_amount = frm.doc.actual_property_amount;
        row.total_expense = expense;
        row.actual_amount = actual_property_amount;
    }
});

// Calculate amount based on contribution
function calculate_row_amount(frm, row) {
    let grossAmount = frm.doc.gross_purchase_amount || 0;
    row.amount = (grossAmount * row.contribution) / 100;
}

// Calculate contribution based on amount
function calculate_row_contribution(frm, row) {
    let grossAmount = frm.doc.gross_purchase_amount || 0;
    row.contribution = grossAmount > 0 ? (row.amount / grossAmount) * 100 : 0;
}

// function calculate_shareholder_amounts(frm) {
//     let grossAmount = frm.doc.gross_purchase_amount || 0;
//     frm.doc.custom_shareholder_table.forEach(row => {
//         calculate_row_amount(frm, row);  // Calculate each row's amount based on contribution
//     });
//     frm.refresh_field("custom_shareholder_table");
// }

function validate_total_contribution(frm) {
    let totalContribution = 0;
    frm.doc.shareholder.forEach(row => {
        totalContribution += row.contribution || 0;
    });

    // if (totalContribution !== 100 && frm.doc.custom_shareholder_table.length > 0) {
    //     frappe.throw(__('The total contribution must be exactly 100%. Current total: ') + totalContribution + '%');
    // }
}
frappe.ui.form.on('Property Shareholder', {
    after_save: function(frm) {
        // Get the main property selected in the current document
        let main_property = frm.doc.property;
        if (!main_property) {
            frappe.msgprint(__('Please select a main property.'));
            return;
        }

        // Fetch all properties where "split_from" matches the main property
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Asset', // Assuming "Property" is stored in Asset
                filters: { split_from: main_property },
                fields: ['name']
            },
            callback: function(response) {
                let properties_to_update = response.message || [];
                let shareholder_data = frm.doc.shareholder || [];

                // Prepare child table data
                let shareholder_entries = shareholder_data.map(row => {
                    return {
                        shareholder_name: row.shareholder_name,
                        contribution: row.contribution,
                        amount: row.amount,
                        is_shareholder_exit:row.is_shareholder_exit,
                        no_expense_included: row.no_expense_included
                    };
                });

                // Update the main property
                update_property_shareholders(main_property, shareholder_entries);

                // Update the properties split from the main property
                properties_to_update.forEach(property => {
                    update_property_shareholders(property.name, shareholder_entries);
                });
            }
        });
    }
});

// Function to append shareholders to a property's "shareholder" child table
function update_property_shareholders(property_name, shareholder_entries) {
    frappe.call({
        method: 'frappe.client.get',
        args: {
            doctype: 'Asset', // Assuming "Property" is stored in Asset
            name: property_name
        },
        callback: function(response) {
            let property = response.message;
            if (property) {
                let existing_shareholders = property.custom_shareholder_table || [];
                existing_shareholders.push(...shareholder_entries);

                // Save the updated property
                frappe.call({
                    method: 'frappe.client.save',
                    args: {
                        doc: {
                            doctype: 'Asset',
                            name: property.name,
                            shareholder: existing_shareholders
                        }
                    },
                    callback: function() {
                        frappe.msgprint(__('Shareholder details updated for property: ' + property_name));
                    }
                });
            }
        }
    });
}
frappe.ui.form.on('Shareholder Property', {
    create_journal_entry_1: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];

        // Validate fields
        if (!row.mode_of_payment) {
            frappe.msgprint(__('Please set the Mode of Payment before creating the Journal Entry.'));
            return;
        }

        if (row.journal_entry) {
            frappe.msgprint(__('A Journal Entry has already been created for this Shareholder.'));
            return;
        }

        if (!row.amount || row.amount <= 0) {
            frappe.msgprint(__('Amount must be greater than zero.'));
            return;
        }

        // Call the server-side function
        frappe.call({
            method: 'property_management.property_management.custom_script.asset.create_shareholder_journal_entry_1',
            args: {
                asset_name: frm.doc.property,
                company: frm.doc.company,
                mode_of_payment: row.mode_of_payment,
                shareholder: row.shareholder,
                shareholder_account: row.shareholder_account,
                amount: row.amount
            },
            callback: function (response) {
                if (response.message) {
                    // Update the child table with the Journal Entry ID
                    frappe.model.set_value(cdt, cdn, 'journal_entry', response.message);
                    frappe.msgprint(__('Journal Entry {0} created and submitted successfully.', [response.message]));
                    frm.refresh_field('custom_shareholder_table');
                }
            }
        });
    }
});