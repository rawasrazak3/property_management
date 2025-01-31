// // Copyright (c) 2025, Ketan Patel and contributors
// // For license information, please see license.txt

// frappe.ui.form.on("Profit Pay", {
//     refresh: function(frm) {
//         if (frm.doc.docstatus == 0){
//             frm.add_custom_button(__('Create Journal Entry'), function() {
//                 open_profit_split_dialog(frm);
//             });
//         }
//     },
// 	property: function (frm) {
//         if (frm.doc.property) {
//             // Fetch assets where custom_against_property matches the selected property
//             frappe.call({
//                 method: 'property_management.property_management.doctype.profit_pay.profit_pay.fetch_assets_with_property_hierarchy',
//                 args: {
//                     property_id: frm.doc.property,
//                     limit_page_length: 100 // Adjust the limit as needed
//                 },
//                 callback: function(r) {
//                     // Clear existing rows in the child table
//                     frm.clear_table('sold_property_table');

//                     // Add fetched assets to the child table, if any
//                     if (r.message && r.message.length > 0) {
//                         r.message.forEach(asset => {
//                             let child = frm.add_child('sold_property_table');
//                             child.property_name = asset.name;
//                             child.property = asset.asset_name;
//                             child.profit = asset.custom_profit;
//                             child.selling_amount = asset.gross_purchase_amount + asset.custom_profit;

//                             // Refresh the child table to show the changes
//                             frm.refresh_field('sold_property_table');
//                         });
//                     }

//                     // Fetch the selected asset's details and add it to the child table
//                     frappe.call({
//                         method: 'frappe.client.get',
//                         args: {
//                             doctype: 'Asset',
//                                 name: frm.doc.property,  // Match against the selected property ID
                            
//                             // name: frm.doc.property  // Fetch the selected property asset details
//                         },
//                         callback: function(r) {
//                             if (r && r.message) {
//                                 let asset = r.message;
//                                 if (asset.status=== 'Sold'){
//                                     // Add the selected asset to the child table
//                                     let child = frm.add_child('sold_property_table');
//                                     child.property_name = asset.name;
//                                     child.profit = asset.custom_profit;
//                                     child.selling_amount = asset.gross_purchase_amount + asset.custom_profit;

//                                     // Refresh the child table to show the changes
//                                     frm.refresh_field('sold_property_table');
//                                 }
//                             }
//                         }
//                     });
//                 }
//             });
//             // Fetch the selected property's shareholders from the child table
//             frappe.call({
//                 method: 'frappe.client.get',
//                 args: {
//                     doctype: 'Asset',  // Fetch the Asset DocType
//                     name: frm.doc.property  // Use the selected property's name
//                 },
//                 callback: function (r) {
//                     if (r.message) {
//                         let property = r.message;

//                         // Apply a dynamic filter to the 'shareholder' field
//                         frm.set_query('shareholder', function () {
//                             return {
//                                 filters: {
//                                     name: ['in', property.custom_shareholder_table.map(row => row.shareholder)]
//                                 }
//                             };
//                         });

//                         // frappe.msgprint(__('Shareholder options have been filtered based on the selected property.'));
//                     } else {
//                         frappe.msgprint(__('No property details found.'));
//                     }
//                 }
//             });
            
//         }
//     },
//     // Trigger when the shareholder is selected
//     shareholder: function (frm) {
//         if (frm.doc.property && frm.doc.shareholder) {
//             // Fetch the selected asset (property)
//             frappe.call({
//                 method: 'frappe.client.get',
//                 args: {
//                     doctype: 'Asset',
//                     name: frm.doc.property  // Match against the selected property ID
//                 },
//                 callback: function(r) {
//                     if (r && r.message) {
//                         let asset = r.message;

//                         // Loop through the 'Shareholder Property' child table in the selected asset
//                         let shareholder_data = null;
//                         asset.custom_shareholder_table.forEach(shareholder_row => {
//                             if (shareholder_row.shareholder === frm.doc.shareholder) {
//                                 // Save matching shareholder data
//                                 shareholder_data = shareholder_row;

//                                 // Update the initial contribution field
//                                 frm.set_value('initial_contribution', shareholder_row.actual_amount);
//                             }
//                         });

//                         // If shareholder data is found, fetch the opening balance from GL Entry
//                         if (shareholder_data) {
//                             frappe.db.get_value(
//                                 'GL Entry', 
//                                 {
//                                     party: frm.doc.shareholder,
//                                     party_type : 'Shareholder',
//                                     account: shareholder_data.shareholder_account, // Replace with the correct account field
//                                     project: asset.custom_project,
//                                     is_opening:'Yes'
//                                 }, 
//                                 'credit as opening_balance'
//                             ).then(balance_response => {
//                                 if (balance_response && balance_response.message) {
//                                     let opening_balance = balance_response.message.opening_balance || 0;

//                                     // Update the contribution field with the sum of shareholder amount and opening balance
//                                     let contribution = (shareholder_data.amount || 0) + opening_balance;
//                                     frm.set_value('contribution', contribution);
//                                 }
//                             });
//                         }
//                     }
//                 }
//             });
//             console.log("properties_list:", getPropertiesFromSoldPropertyTable());
//             frappe.call({
//                 method: "property_management.property_management.doctype.profit_pay.profit_pay.fetch_filtered_asset",
//                 args: {
//                     property_id: frm.doc.property,
//                     shareholder_name: frm.doc.shareholder,
//                     properties_list: getPropertiesFromSoldPropertyTable(),  // Get the properties from the child table
//                     limit_page_length: 100
//                 },
//                 callback: function(response) {
//                     console.log("entries:", response.message);
//                     const unique_assets = response.message || [];
//                     frm.clear_table("sold_property_table");
//                     unique_assets.forEach(asset => {
//                         let child = frm.add_child("sold_property_table");
//                         child.property_name = asset.asset_id;
//                             child.property = asset.asset_name;
//                             child.profit = asset.custom_profit;
//                             child.selling_amount = asset.gross_purchase_amount + asset.custom_profit;

//                             // Refresh the child table to show the changes
//                             frm.refresh_field('sold_property_table');
//                     });
//                     // frm.refresh_field("sold_property_table");
//                 }
//             });
//         }
//     }
// });
// function open_profit_split_dialog(frm) {
//     frappe.prompt([
//         {
//             label: 'Mode of Payment',
//             fieldname: 'mode_of_payment',
//             fieldtype: 'Link',
//             options: 'Mode of Payment',
//             reqd: 1
//         }
//     ],
//     function(values) {
//         create_journal_entry(frm, values.mode_of_payment);
//     },
//     __('Select Mode of Payment'),
//     __('Proceed'));
// }

// function create_journal_entry(frm, mode_of_payment) {
//     frappe.call({
//         method: "property_management.property_management.doctype.profit_pay.profit_pay.create_profit_payout_journal",
//         args: {
//             profit_pay_id: frm.doc.name,
//             mode_of_payment: mode_of_payment
//         },
//         callback: function(response) {
//             if (response.message) {
//                 frappe.set_route('Form', 'Journal Entry', response.message);
//             }
//         }
//     });
// }
// // Function to get properties from the Sold Property Details table (assuming you are using the current Profit Pay document)
// function getPropertiesFromSoldPropertyTable() {
//     let properties = [];
//     // Loop through the child table of the current Profit Pay document
//     // Replace this with the actual logic to get the properties from the Profit Pay doc.
//     let soldProperties = cur_frm.doc.sold_property_table || []; // assuming 'sold_property_details' is the child table name

//     soldProperties.forEach(property => {
//         properties.push({
//             property_name: property.property_name  // Assuming the field for property name is 'property_name'
//         });
//     });
//     console.log("properties",properties);
//     return properties;
// }