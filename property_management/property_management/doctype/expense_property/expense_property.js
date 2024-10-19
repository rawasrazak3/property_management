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
                        custom_against_property: frm.doc.property  // Match against the selected property ID
                    },
                    fields: ['name', 'gfa_sqft', 'gross_purchase_amount']  // Fields to fetch
                },
                callback: function(r) {
                    // Clear existing rows in the child table
                    frm.clear_table('land_property');

                    if (r.message && r.message.length > 0) {
                        // Add fetched assets to the child table
                        r.message.forEach(asset => {
                            let child = frm.add_child('land_property');
                            child.property = asset.name;
                            child.gfa_sqft = asset.gfa_sqft;
                            child.gross_amount = asset.gross_purchase_amount;
                        });
                    } else {
                        // If no data is fetched for custom_against_property, fetch the selected asset's details
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

                    // Refresh the child table to show the changes
                    frm.refresh_field('land_property');
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
