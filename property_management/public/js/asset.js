frappe.ui.form.on("Asset", "address", function(frm, cdt, cdn) {
    if (frm.doc.address){
        return frm.call({
            method: "frappe.contacts.doctype.address.address.get_address_display",
            args: {
                "address_dict": frm.doc.address
            },
            callback: function(r) {
                if(r.message)
                frm.set_value("address_display", r.message);
            }
        });
    }
    else {
        frm.set_value("address_display", "");
    }
});

frappe.ui.form.on("Asset", {
    setup: function(frm) {
        frm.set_query("address", function() {
            return {
                filters: [
                    ["Dynamic Link","link_doctype", "=", "Customer"],
                    ["Dynamic Link","link_name", "=", frm.doc.property_manager]
                ]
            };
        });
    }
});


frappe.ui.form.on("Asset", {
    setup: function(frm) {
        frm.set_query("contact", function() {
            return {
                filters: [
                    ["Dynamic Link","link_doctype", "=", "Customer"],
                    ["Dynamic Link","link_name", "=", frm.doc.property_manager]
                ]
            };
        });
    }
});

frappe.ui.form.on("Asset", {
    before_save: function(frm) {
        // frm.set_value('gfa_m', frm.doc.gfa_sqft * 0.092903);
        frm.set_value('total_price', frm.doc.gfa_m * frm.doc.unit_price);
    }
});


frappe.ui.form.on('Property Insurance', {
    form_render(frm, cdt, cdn){
        frm.fields_dict.property_insurance.grid.wrapper.find('.btn-attach').addClass("btn-primary").removeClass("btn-default");
    }
});


frappe.ui.form.on('Floor Plan', {
    form_render(frm, cdt, cdn){
        frm.fields_dict.floor_plan.grid.wrapper.find('.btn-attach').addClass("btn-primary").removeClass("btn-default");
    }
});


frappe.ui.form.on('Photos', {
    form_render(frm, cdt, cdn){
        frm.fields_dict.photos.grid.wrapper.find('.btn-attach').addClass("btn-primary").removeClass("btn-default");
    }
});


frappe.ui.form.on('Documents', {
    form_render(frm, cdt, cdn){
        frm.fields_dict.documents.grid.wrapper.find('.btn-attach').addClass("btn-primary").removeClass("btn-default");
    }
});


frappe.ui.form.on("Asset", "before_save", function(frm, cdt, cdn) {
    $.each(frm.doc.finance_books || [], function(i, d) {
        var end_date = frappe.datetime.add_months(d.depreciation_start_date, (d.total_number_of_depreciations * d.frequency_of_depreciation) - 1);
        frm.set_value('start_date', d.depreciation_start_date);
        frm.set_value('end_date', end_date);
    });
});


frappe.ui.form.on('Asset', {
    rent_type: function(frm) {
        frm.set_value('calculate_depreciation', 1);
        if (frm.doc.opening_accumulated_depreciation === 0) {
            frm.clear_table('finance_books');
            var d = frm.add_child("finance_books");
            d.depreciation_method="Manual";
            if (frm.doc.rent_type == "Monthly") {
                d.total_number_of_depreciations = 12;
                d.frequency_of_depreciation = 1;
                d.depreciation_start_date = frappe.datetime.add_months(frm.doc.available_for_use_date, 1);
                d.expected_value_after_useful_life = 0;
            }
            else if (frm.doc.rent_type == "Quarterly") {
                d.total_number_of_depreciations = 4;
                d.frequency_of_depreciation = 3;
                d.depreciation_start_date = frappe.datetime.add_months(frm.doc.available_for_use_date, 3);
                d.expected_value_after_useful_life = 0;
            }
            else if (frm.doc.rent_type == "Half-yearly") {
                d.total_number_of_depreciations = 2;
                d.frequency_of_depreciation = 6;
                d.depreciation_start_date = frappe.datetime.add_months(frm.doc.available_for_use_date, 6);
                d.expected_value_after_useful_life = 0;
            }
            else if (frm.doc.rent_type == "Yearly") {
                d.total_number_of_depreciations = 1;
                d.frequency_of_depreciation = 12;
                d.depreciation_start_date = frappe.datetime.add_months(frm.doc.available_for_use_date, 12);
                d.expected_value_after_useful_life = 0;
            }
            frm.refresh_fields("finance_books");
        }
        else if (frm.doc.opening_accumulated_depreciation !== 0) {
            frm.clear_table('finance_books');
            var d = frm.add_child("finance_books");
            d.depreciation_method="Manual";
            if (frm.doc.rent_type == "Monthly") {
                d.total_number_of_depreciations = 12;
                d.frequency_of_depreciation = 1;
                d.depreciation_start_date = frappe.datetime.add_months(frm.doc.available_for_use_date, 1);
                d.expected_value_after_useful_life = frm.doc.opening_accumulated_depreciation;
            }
            else if (frm.doc.rent_type == "Quarterly") {
                d.total_number_of_depreciations = 4;
                d.frequency_of_depreciation = 3;
                d.depreciation_start_date = frappe.datetime.add_months(frm.doc.available_for_use_date, 3);
                d.expected_value_after_useful_life = frm.doc.opening_accumulated_depreciation;
            }
            else if (frm.doc.rent_type == "Half-yearly") {
                d.total_number_of_depreciations = 2;
                d.frequency_of_depreciation = 6;
                d.depreciation_start_date = frappe.datetime.add_months(frm.doc.available_for_use_date, 6);
                d.expected_value_after_useful_life = frm.doc.opening_accumulated_depreciation;
            }
            else if (frm.doc.rent_type == "Yearly") {
                d.total_number_of_depreciations = 1;
                d.frequency_of_depreciation = 12;
                d.depreciation_start_date = frappe.datetime.add_months(frm.doc.available_for_use_date, 12);
                d.expected_value_after_useful_life = frm.doc.opening_accumulated_depreciation;
            }
            frm.refresh_fields("finance_books");
        }
    },

    available_for_use_date: function(frm) {
        if (frm.doc.calculate_depreciation === 1 && frm.doc.opening_accumulated_depreciation === 0) {
            frm.clear_table('finance_books');
            var d = frm.add_child("finance_books");
            d.depreciation_method="Manual";
            if (frm.doc.rent_type == "Monthly") {
                d.total_number_of_depreciations = 12;
                d.frequency_of_depreciation = 1;
                d.depreciation_start_date = frappe.datetime.add_months(frm.doc.available_for_use_date, 1);
                d.expected_value_after_useful_life = 0;
            }
            else if (frm.doc.rent_type == "Quarterly") {
                d.total_number_of_depreciations = 4;
                d.frequency_of_depreciation = 3;
                d.depreciation_start_date = frappe.datetime.add_months(frm.doc.available_for_use_date, 3);
                d.expected_value_after_useful_life = 0;
            }
            else if (frm.doc.rent_type == "Half-yearly") {
                d.total_number_of_depreciations = 2;
                d.frequency_of_depreciation = 6;
                d.depreciation_start_date = frappe.datetime.add_months(frm.doc.available_for_use_date, 6);
                d.expected_value_after_useful_life = 0;
            }
            else if (frm.doc.rent_type == "Yearly") {
                d.total_number_of_depreciations = 1;
                d.frequency_of_depreciation = 12;
                d.depreciation_start_date = frappe.datetime.add_months(frm.doc.available_for_use_date, 12);
                d.expected_value_after_useful_life = 0;
            }
            frm.refresh_fields("finance_books");
        }
        else if (frm.doc.calculate_depreciation === 1 && frm.doc.opening_accumulated_depreciation !== 0) {
            frm.clear_table('finance_books');
            var d = frm.add_child("finance_books");
            d.depreciation_method="Manual";
            if (frm.doc.rent_type == "Monthly") {
                d.total_number_of_depreciations = 12;
                d.frequency_of_depreciation = 1;
                d.depreciation_start_date = frappe.datetime.add_months(frm.doc.available_for_use_date, 1);
                d.expected_value_after_useful_life = frm.doc.opening_accumulated_depreciation;
            }
            else if (frm.doc.rent_type == "Quarterly") {
                d.total_number_of_depreciations = 4;
                d.frequency_of_depreciation = 3;
                d.depreciation_start_date = frappe.datetime.add_months(frm.doc.available_for_use_date, 3);
                d.expected_value_after_useful_life = frm.doc.opening_accumulated_depreciation;
            }
            else if (frm.doc.rent_type == "Half-yearly") {
                d.total_number_of_depreciations = 2;
                d.frequency_of_depreciation = 6;
                d.depreciation_start_date = frappe.datetime.add_months(frm.doc.available_for_use_date, 6);
                d.expected_value_after_useful_life = frm.doc.opening_accumulated_depreciation;
            }
            else if (frm.doc.rent_type == "Yearly") {
                d.total_number_of_depreciations = 1;
                d.frequency_of_depreciation = 12;
                d.depreciation_start_date = frappe.datetime.add_months(frm.doc.available_for_use_date, 12);
                d.expected_value_after_useful_life = frm.doc.opening_accumulated_depreciation;
            }
            frm.refresh_fields("finance_books");
        }
    },

    opening_accumulated_depreciation: function(frm) {
        if (frm.doc.calculate_depreciation === 1 && frm.doc.opening_accumulated_depreciation === 0) {
            frm.clear_table('finance_books');
            var d = frm.add_child("finance_books");
            d.depreciation_method="Manual";
            if (frm.doc.rent_type == "Monthly") {
                d.total_number_of_depreciations = 12;
                d.frequency_of_depreciation = 1;
                d.depreciation_start_date = frappe.datetime.add_months(frm.doc.available_for_use_date, 1);
                d.expected_value_after_useful_life = 0;
            }
            else if (frm.doc.rent_type == "Quarterly") {
                d.total_number_of_depreciations = 4;
                d.frequency_of_depreciation = 3;
                d.depreciation_start_date = frappe.datetime.add_months(frm.doc.available_for_use_date, 3);
                d.expected_value_after_useful_life = 0;
            }
            else if (frm.doc.rent_type == "Half-yearly") {
                d.total_number_of_depreciations = 2;
                d.frequency_of_depreciation = 6;
                d.depreciation_start_date = frappe.datetime.add_months(frm.doc.available_for_use_date, 6);
                d.expected_value_after_useful_life = 0;
            }
            else if (frm.doc.rent_type == "Yearly") {
                d.total_number_of_depreciations = 1;
                d.frequency_of_depreciation = 12;
                d.depreciation_start_date = frappe.datetime.add_months(frm.doc.available_for_use_date, 12);
                d.expected_value_after_useful_life = 0;
            }
            frm.refresh_fields("finance_books");
        }
        else if (frm.doc.calculate_depreciation === 1 && frm.doc.opening_accumulated_depreciation !== 0) {
            frm.clear_table('finance_books');
            var d = frm.add_child("finance_books");
            d.depreciation_method="Manual";
            if (frm.doc.rent_type == "Monthly") {
                d.total_number_of_depreciations = 12;
                d.frequency_of_depreciation = 1;
                d.depreciation_start_date = frappe.datetime.add_months(frm.doc.available_for_use_date, 1);
                d.expected_value_after_useful_life = frm.doc.opening_accumulated_depreciation;
            }
            else if (frm.doc.rent_type == "Quarterly") {
                d.total_number_of_depreciations = 4;
                d.frequency_of_depreciation = 3;
                d.depreciation_start_date = frappe.datetime.add_months(frm.doc.available_for_use_date, 3);
                d.expected_value_after_useful_life = frm.doc.opening_accumulated_depreciation;
            }
            else if (frm.doc.rent_type == "Half-yearly") {
                d.total_number_of_depreciations = 2;
                d.frequency_of_depreciation = 6;
                d.depreciation_start_date = frappe.datetime.add_months(frm.doc.available_for_use_date, 6);
                d.expected_value_after_useful_life = frm.doc.opening_accumulated_depreciation;
            }
            else if (frm.doc.rent_type == "Yearly") {
                d.total_number_of_depreciations = 1;
                d.frequency_of_depreciation = 12;
                d.depreciation_start_date = frappe.datetime.add_months(frm.doc.available_for_use_date, 12);
                d.expected_value_after_useful_life = frm.doc.opening_accumulated_depreciation;
            }
            frm.refresh_fields("finance_books");
        }
    }    
    
});

frappe.ui.form.on('Asset', {
    refresh(frm) {
        console.log("Test ::::::::::::::::::::::")
        frm.set_df_property('depreciation_schedule_sb', 'hide', 1)
        frm.add_custom_button(__("Available"), function() {
            frm.set_value('property_status', "Available");
            frm.save();
            if (frm.doc.docstatus == 1 ) {
                frm.save('Update');
            }
        },__("Property Status"));
        frm.add_custom_button(__("Rent/Lease"), function() {
            frm.set_value('property_status', "Rent/Lease");
            frm.save();
            if (frm.doc.docstatus == 1) {
                frm.save('Update');
            }
        },__("Property Status"));
        frm.add_custom_button(__("Booked"), function() {
            frm.set_value('property_status', "Booked");
            frm.save();
            if (frm.doc.docstatus == 1) {
                frm.save('Update');
            }
        },__("Property Status"));
        frm.add_custom_button(__("Closed"), function() {
            frm.set_value('property_status', "Closed");
            frm.save();
            if (frm.doc.docstatus == 1) {
                frm.save('Update');
            }
        },__("Property Status"));

        if (frm.doc.docstatus == 1&&frm.doc.custom_property_type==="Rent"&&frm.doc.property_status=="Available") {
            frm.page.set_inner_btn_group_as_primary(__("Create"));
            frm.add_custom_button(__("Tenancy"), function() {
                    frappe.route_options = {
                        "asset": frm.doc.name
                    };
                    frappe.set_route("tenancy", "new-tenancy");
            }, __("Create"));
        }
    }
});

frappe.ui.form.on('Asset', {
    refresh: function(frm) {
        // Ensure that the buttons are only added on form view (refresh trigger)
        if (!frm.is_new() && frm.doc.custom_property_type=='Land') {
            // Create a button group named 'Property'
            frm.add_custom_button(__('Property'), null, 'Actions');

            // Add "Bulk Asset Split" button to the 'Property' dropdown group
            frm.add_custom_button(__('Bulk Asset Split'), () => {
                open_bulk_asset_split_dialog(frm);
            }, __('Property'));

            // Add "Shareholder Exit" button to the 'Property' dropdown group
            frm.add_custom_button(__('Shareholder Exit'), () => {
                show_shareholder_exit_dialog(frm);
            }, __('Property'));

            // Add "Profit Split" button to the 'Property' dropdown group, only if status is "Sold"
            if (frm.doc.status === 'Sold') {
                frm.add_custom_button(__('Profit Split'), () => {
                    open_profit_split_dialog(frm);
                }, __('Property'));
            }
        }
    }
});

// frappe.ui.form.on('Asset', {
//     refresh: function(frm) {
//         // Show button only if asset status is "Sold"
//         if (frm.doc.status === 'Sold') {
//             frm.add_custom_button(__('Profit Split'), () => {
//                 open_profit_split_dialog(frm);
//             });
//         }
//     }
// });

// frappe.ui.form.on('Asset', {
//     refresh: function(frm) {
//         frm.add_custom_button(__('Bulk Asset Split'), () => {
//             open_bulk_asset_split_dialog(frm);
//         });
//     }
// });

// function open_bulk_asset_split_dialog(frm) {
//     const unit_price = frm.doc.gross_purchase_amount / frm.doc.asset_quantity;

//     const dialog = new frappe.ui.Dialog({
//         title: 'Bulk Asset Split',
//         fields: [
//             {fieldname: 'item_code', label: 'Item', fieldtype: 'Data', default: frm.doc.item_code, read_only: 1},
//             {fieldname: 'gross_purchase_amount', label: 'Gross Purchase Amount', fieldtype: 'Currency', default: frm.doc.gross_purchase_amount, read_only: 1},
//             {fieldname: 'asset_quantity', label: 'Asset Quantity', fieldtype: 'Float', default: frm.doc.asset_quantity, read_only: 1},
//             {fieldname: 'unit_price', label: 'Unit Price', fieldtype: 'Currency', default: unit_price, read_only: 1},
//             {
//                 fieldname: 'name_prefix',
//                 label: 'Name Prefix',
//                 fieldtype: 'Data',
//                 description: 'Prefix for new asset names'
//             },
//             {
//                 fieldname: 'number_of_splits',
//                 label: 'Number of Splits',
//                 fieldtype: 'Int',
//                 description: 'Enter the number of rows for splitting the asset'
//             },
//             {
//                 fieldname: 'split_details',
//                 label: 'Split Details',
//                 fieldtype: 'Table',
//                 fields: [
//                     {fieldname: 'quantity_to_split', label: 'Quantity to Split', fieldtype: 'Float', in_list_view: 1, reqd: 1},
//                     {fieldname: 'gross_amount', label: 'Gross Amount', fieldtype: 'Currency', in_list_view: 1, read_only: 1}
//                 ],
//                 data: [],
//                 get_data: () => dialog.get_value('split_details')
//             }
//         ],
//         primary_action_label: 'Submit',
//         primary_action: (values) => {
//             // Disable the Submit button to prevent multiple clicks
//             dialog.get_primary_btn().prop('disabled', true);

//             frappe.call({
//                 method: 'property_management.property_management.custom_script.asset.bulk_asset_split',
//                 args: {
//                     asset_name: frm.doc.name,
//                     name_prefix: values.name_prefix, // Pass the prefix to the server
//                     split_details: JSON.stringify(values.split_details)
//                 },
//                 callback: function(response) {
//                     frappe.msgprint(__('Bulk Asset Split completed successfully.'));
//                     dialog.hide(); // Close the dialog
//                     frm.reload_doc(); // Reload the document to reflect changes
//                 },
//                 error: function() {
//                     // Re-enable the Submit button if an error occurs
//                     dialog.get_primary_btn().prop('disabled', false);
//                 }
//             });
//         }
//     });

//     dialog.fields_dict.number_of_splits.$input.on('change', function() {
//         const number_of_splits = dialog.get_value('number_of_splits');
//         const split_details = [];
        
//         if (number_of_splits && number_of_splits > 0) {
//             const split_quantity = frm.doc.asset_quantity / number_of_splits;
            
//             for (let i = 0; i < number_of_splits; i++) {
//                 split_details.push({
//                     quantity_to_split: split_quantity,
//                     gross_amount: split_quantity * unit_price
//                 });
//             }
            
//             dialog.fields_dict.split_details.grid.df.data = split_details;
//             dialog.fields_dict.split_details.grid.refresh();
//         }
//     });

//     dialog.fields_dict.split_details.grid.wrapper.on('change', 'input[data-fieldname="quantity_to_split"]', function(e) {
//         const split_details = dialog.get_value('split_details');
        
//         split_details.forEach(row => {
//             if (row.quantity_to_split) {
//                 row.gross_amount = row.quantity_to_split * unit_price;
//             } else {
//                 row.gross_amount = 0;
//             }
//         });
        
//         dialog.fields_dict.split_details.grid.refresh();
//     });

//     dialog.show();
// }

// function open_bulk_asset_split_dialog(frm) {
//     const unit_price = frm.doc.gross_purchase_amount / frm.doc.asset_quantity;

//     const dialog = new frappe.ui.Dialog({
//         title: 'Bulk Asset Split',
//         fields: [
//             {fieldname: 'item_code', label: 'Item', fieldtype: 'Data', default: frm.doc.item_code, read_only: 1},
//             {fieldname: 'gross_purchase_amount', label: 'Gross Purchase Amount', fieldtype: 'Currency', default: frm.doc.gross_purchase_amount, read_only: 1},
//             {fieldname: 'asset_quantity', label: 'Asset Quantity', fieldtype: 'Float', default: frm.doc.asset_quantity, read_only: 1},
//             {fieldname: 'unit_price', label: 'Unit Price', fieldtype: 'Currency', default: unit_price, read_only: 1},
//             {
//                 fieldname: 'name_prefix',
//                 label: 'Name Prefix',
//                 fieldtype: 'Data',
//                 description: 'Prefix for new asset names'
//             },
//             {
//                 fieldname: 'number_of_splits',
//                 label: 'Number of Splits',
//                 fieldtype: 'Int',
//                 description: 'Enter the number of rows for splitting the asset'
//             },
//             {
//                 fieldname: 'split_details',
//                 label: 'Split Details',
//                 fieldtype: 'Table',
//                 fields: [
//                     {fieldname: 'name_prefix', label: 'Name Prefix', fieldtype: 'Data', in_list_view: 1},
//                     {fieldname: 'quantity_to_split', label: 'Quantity to Split', fieldtype: 'Float', in_list_view: 1, reqd: 1},
//                     {fieldname: 'gross_amount', label: 'Gross Amount', fieldtype: 'Currency', in_list_view: 1, read_only: 1}
//                 ],
//                 data: [],
//                 get_data: () => dialog.get_value('split_details')
//             }
//         ],
//         primary_action_label: 'Submit',
//         primary_action: (values) => {
//             // Disable the Submit button to prevent multiple clicks
//             dialog.get_primary_btn().prop('disabled', true);

//             frappe.call({
//                 method: 'property_management.property_management.custom_script.asset.bulk_asset_split',
//                 args: {
//                     asset_name: frm.doc.name,
//                     split_details: JSON.stringify(values.split_details)
//                 },
//                 callback: function(response) {
//                     frappe.msgprint(__('Bulk Asset Split completed successfully.'));
//                     dialog.hide(); // Close the dialog
//                     frm.reload_doc(); // Reload the document to reflect changes
//                 },
//                 error: function() {
//                     // Re-enable the Submit button if an error occurs
//                     dialog.get_primary_btn().prop('disabled', false);
//                 }
//             });
//         }
//     });

//     // Auto-generate split details based on number of splits
//     dialog.fields_dict.number_of_splits.$input.on('change', function() {
//         const number_of_splits = dialog.get_value('number_of_splits');
//         const main_name_prefix = dialog.get_value('name_prefix');
//         const split_details = [];

//         if (number_of_splits && number_of_splits > 0) {
//             const split_quantity = frm.doc.asset_quantity / number_of_splits;

//             for (let i = 0; i < number_of_splits; i++) {
//                 split_details.push({
//                     name_prefix: `${main_name_prefix} ${i + 1}`, // Generate name prefix based on main input
//                     quantity_to_split: split_quantity,
//                     gross_amount: split_quantity * unit_price
//                 });
//             }

//             dialog.fields_dict.split_details.grid.df.data = split_details;
//             dialog.fields_dict.split_details.grid.refresh();
//         }
//     });

//     // Update gross amount when quantity changes
//     dialog.fields_dict.split_details.grid.wrapper.on('change', 'input[data-fieldname="quantity_to_split"]', function(e) {
//         const unit_price = frm.doc.gross_purchase_amount / frm.doc.asset_quantity;
//         const split_details = dialog.get_value('split_details');

//         split_details.forEach(row => {
//             if (row.quantity_to_split) {
//                 row.gross_amount = row.quantity_to_split * unit_price;
//             } else {
//                 row.gross_amount = 0;
//             }
//         });

//         dialog.fields_dict.split_details.grid.refresh();
//     });

//     dialog.show();
// }
function open_bulk_asset_split_dialog(frm) {
    const unit_price = frm.doc.gross_purchase_amount / frm.doc.asset_quantity;

    const dialog = new frappe.ui.Dialog({
        title: 'Bulk Asset Split',
        fields: [
            {fieldname: 'item_code', label: 'Item', fieldtype: 'Data', default: frm.doc.item_code, read_only: 1},
            {fieldname: 'gross_purchase_amount', label: 'Gross Purchase Amount', fieldtype: 'Currency', default: frm.doc.gross_purchase_amount, read_only: 1},
            {fieldname: 'asset_quantity', label: 'Asset Quantity', fieldtype: 'Float', default: frm.doc.asset_quantity, read_only: 1},
            {fieldname: 'unit_price', label: 'Unit Price', fieldtype: 'Currency', default: unit_price, read_only: 1},
            {
                fieldname: 'name_prefix',
                label: 'Name Prefix',
                fieldtype: 'Data',
                description: 'Prefix for new asset names'
            },
            {
                fieldname: 'number_of_splits',
                label: 'Number of Splits',
                fieldtype: 'Int',
                description: 'Enter the number of rows for splitting the asset (excluding the main property)'
            },
            {
                fieldname: 'split_details',
                label: 'Split Details',
                fieldtype: 'Table',
                fields: [
                    {fieldname: 'name_prefix', label: 'Name Prefix', fieldtype: 'Data', in_list_view: 1},
                    {fieldname: 'quantity_to_split', label: 'Quantity to Split', fieldtype: 'Float', in_list_view: 1, reqd: 1},
                    {fieldname: 'gross_amount', label: 'Gross Amount', fieldtype: 'Currency', in_list_view: 1, read_only: 1}
                ],
                data: [],
                get_data: () => dialog.get_value('split_details')
            }
        ],
        primary_action_label: 'Submit',
        primary_action: (values) => {
            // Disable the Submit button to prevent multiple clicks
            dialog.get_primary_btn().prop('disabled', true);

            frappe.call({
                method: 'property_management.property_management.custom_script.asset.bulk_asset_split',
                args: {
                    asset_name: frm.doc.name,
                    split_details: JSON.stringify(values.split_details)
                },
                callback: function(response) {
                    frappe.msgprint(__('Bulk Asset Split completed successfully.'));
                    dialog.hide(); // Close the dialog
                    frm.reload_doc(); // Reload the document to reflect changes
                },
                error: function() {
                    // Re-enable the Submit button if an error occurs
                    dialog.get_primary_btn().prop('disabled', false);
                }
            });
        }
    });

    // Auto-generate split details based on number of splits
    dialog.fields_dict.number_of_splits.$input.on('change', function() {
        const number_of_splits = dialog.get_value('number_of_splits');
        const main_name_prefix = dialog.get_value('name_prefix');
        const split_details = [];

        if (number_of_splits && number_of_splits > 0) {
            const adjusted_splits = number_of_splits; // Exclude the last property
            const split_quantity = frm.doc.asset_quantity / (adjusted_splits + 1);

            for (let i = 0; i < adjusted_splits; i++) {
                split_details.push({
                    name_prefix: `${main_name_prefix} ${i + 1}`, // Generate name prefix based on main input
                    quantity_to_split: split_quantity,
                    gross_amount: split_quantity * unit_price
                });
            }

            dialog.fields_dict.split_details.grid.df.data = split_details;
            dialog.fields_dict.split_details.grid.refresh();
        }
    });

    // Update gross amount when quantity changes
    dialog.fields_dict.split_details.grid.wrapper.on('change', 'input[data-fieldname="quantity_to_split"]', function(e) {
        const split_details = dialog.get_value('split_details');

        split_details.forEach(row => {
            if (row.quantity_to_split) {
                row.gross_amount = row.quantity_to_split * unit_price;
            } else {
                row.gross_amount = 0;
            }
        });

        dialog.fields_dict.split_details.grid.refresh();
    });

    dialog.show();
}


frappe.ui.form.on('Asset', {
    refresh: function (frm) {
        if(frm.doc.docstatus===1&&frm.doc.custom_property_type==="Rent"&&frm.doc.property_status=="Available"){
            frm.add_custom_button(__('Multi Property'), function () {
                // Redirect to the Multi Property doctype with pre-filled data
                frappe.new_doc('Multi Property', {
                    property: frm.doc.name,  // Pass the current Asset's name
                    item_code: frm.doc.item_code,
                    item_name: frm.doc.item_name,
                    qty: frm.doc.gfa_m,
                    gross_amount: frm.doc.gross_purchase_amount,
                    available_for_use: frm.doc.available_for_use_date,
                    purchase_date: frm.doc.purchase_date,
                    property_manager: frm.property_manager

                });
            }, __('Create'));
        }
        
    }
});

//////////////////////////////////
// frappe.ui.form.on('Asset', {
//     refresh: function(frm) {
//         calculate_shareholder_amounts(frm);
//     },
//     // gross_purchase_amount: function(frm) {
//     //     calculate_shareholder_amounts(frm);
//     // },
//     update_before_submit: function(frm) {
//         validate_total_contribution(frm);
//     },
//     before_submit: function(frm) {
//         validate_total_contribution(frm);
//     }
// });

// frappe.ui.form.on('Shareholder Property', {
//     contribution: function(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];
//         calculate_row_amount(frm, row);
//         frm.refresh_field("custom_shareholder_table");
//         validate_total_contribution(frm);  // Validate after updating a row
//     },
//     amount: function(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];
//         calculate_row_contribution(frm, row);
//         frm.refresh_field("custom_shareholder_table");
//         validate_total_contribution(frm);  // Validate after updating a row
//     }
// });

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

function calculate_shareholder_amounts(frm) {
    let grossAmount = frm.doc.gross_purchase_amount || 0;
    frm.doc.custom_shareholder_table.forEach(row => {
        calculate_row_amount(frm, row);  // Calculate each row's amount based on contribution
    });
    frm.refresh_field("custom_shareholder_table");
}

function validate_total_contribution(frm) {
    let totalContribution = 0;
    frm.doc.custom_shareholder_table.forEach(row => {
        totalContribution += row.contribution || 0;
    });

    // if (totalContribution !== 100 && frm.doc.custom_shareholder_table.length > 0) {
    //     frappe.throw(__('The total contribution must be exactly 100%. Current total: ') + totalContribution + '%');
    // }
}



///////////////////////////////////////

function show_shareholder_exit_dialog(frm) {
    let shareholders = frm.doc.custom_shareholder_table.map(row => ({
        label: row.shareholder,
        value: row.shareholder
    }));

    // Show the dialog
    let dialog = new frappe.ui.Dialog({
        title: __('Shareholder Exit'),
        fields: [
            {
                label: 'Shareholder',
                fieldname: 'shareholder',
                fieldtype: 'Select',
                options: shareholders,
                reqd: 1
            },
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
                method: "property_management.property_management.custom_script.asset.create_shareholder_exit_journal_entry",
                args: {
                    asset: frm.doc.name,
                    shareholder: values.shareholder,
                    mode_of_payment: values.mode_of_payment
                },
                callback: function(response) {
                    if (response.message) {
                        frappe.set_route("Form", "Journal Entry", response.message);  // Redirect to the Journal Entry
                    }
                }
            });
        }
    });

    dialog.show();
}

////////////////////////////////////////////////////
// frappe.ui.form.on('Asset', {
//     refresh: function(frm) {
//         // Show button only if asset status is "Sold"
//         if (frm.doc.status === 'Sold') {
//             frm.add_custom_button(__('Profit Split'), () => {
//                 open_profit_split_dialog(frm);
//             });
//         }
//     }
// });

function open_profit_split_dialog(frm) {
    frappe.prompt([
        {
            label: 'Mode of Payment',
            fieldname: 'mode_of_payment',
            fieldtype: 'Link',
            options: 'Mode of Payment',
            reqd: 1
        }
    ],
    function(values) {
        create_journal_entry(frm, values.mode_of_payment);
    },
    __('Select Mode of Payment'),
    __('Proceed'));
}

function create_journal_entry(frm, mode_of_payment) {
    frappe.call({
        method: "property_management.property_management.custom_script.asset.create_journal_entry",
        args: {
            asset_id: frm.doc.name,
            mode_of_payment: mode_of_payment
        },
        callback: function(response) {
            if (response.message) {
                frappe.set_route('Form', 'Journal Entry', response.message);
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
                asset_name: frm.doc.name,
                company: frm.doc.company,
                mode_of_payment: row.mode_of_payment,
                shareholder: row.shareholder,
                shareholder_account: row.shareholder_account,
                amount: row.amount,
                project: frm.doc.custom_project
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

frappe.ui.form.on('Asset', {
	custom_property_type:function(frm) {
	    if(frm.doc.custom_property_type === "Rent"){
	        frm.set_value('is_existing_asset',1);
	    }
	    else{
            frm.set_value('is_existing_asset',0);
        }   
	    
		// your code here
	}
});
frappe.ui.form.on('Asset', {
    onload: function(frm) {
        frm.set_query('custom_tenant', function() {
            return {
                filters: {
                    'is_tenant': 1  
                }
            };
        });
    }
});
frappe.ui.form.on('Asset', {
    custom_property_type: function(frm) {
        if (frm.doc.custom_property_type === "Rent") {
            // Filter for Property Unit
            frm.set_query('custom_property_unit', function() {
                return {
                    filters: {
                        parent_item_group: "PROPERTY RENTAL MASTER"
                    }
                };
            });

            // Filter for Property Sub Unit
            frm.set_query('custom_property_subunit', function() {
                return {
                    filters: {
                        parent_item_group: "PROPERTY RENTAL MASTER"
                    }
                };
            });
            // Add a filter to property_item_code based on parent item group
            frm.set_query('item_code', function() {
                return {
                    filters: {
                        item_group: ['in', get_property_rental_item_groups()]
                    }
                };
            });
        } else {
            // Clear filters for other property types
            frm.set_query('custom_property_unit', function() {
                return {};
            });

            frm.set_query('custom_property_subunit', function() {
                return {};
            });

            frm.set_query('item_code', function() {
                return {
                    filters: {
                        item_group:"Land for Sale"
                    }
                };
            });
        }
    }
});
frappe.ui.form.on('Asset', {
    custom_property_owner: function(frm) {
        // Update property_owner when supplier changes, if asset_owner is "Supplier"
        if (frm.doc.asset_owner === "Supplier") {
            frm.set_value('supplier', frm.doc.custom_property_owner);
        }
    }
});

// Helper function to fetch item groups under "PROPERTY RENTAL MASTER"
function get_property_rental_item_groups() {
    let rental_item_groups = [];
    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Item Group",
            fields: ["name"],
            filters: {
                parent_item_group: "PROPERTY RENTAL MASTER"
            }
        },
        async: false,
        callback: function(response) {
            if (response.message) {
                rental_item_groups = response.message.map(group => group.name);
            }
        }
    });
    return rental_item_groups;
}
