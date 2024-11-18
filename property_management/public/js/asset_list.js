frappe.listview_settings['Asset'] = {
	refresh: function(frm) {
        $('*[data-filter="property_status,=,Closed"]').css({'color':'#e24c4c', 'background':'#fff5f5'}); // red
        $('*[data-filter="property_status,=,Rent/Lease"]').css({'color':'#f8814f', 'background':'#fff5f0'}); // orange
        $('*[data-filter="property_status,=,Booked"]').css({'color':'#1579d0', 'background':'#D3E9FA'}); // blue
        $('*[data-filter="property_status,=,Available"]').css({'color':'#2f9d58', 'background':'#eaf5ee'}); // green
	}
};

frappe.listview_settings['Asset'] = {
    refresh: function (listview) {
        // Add a custom action button for creating multi-property sub-units
        listview.page.add_action_item(__("Create Multi Property"), () => {
            // Get the selected assets from the list view
            let selected_assets = listview.get_checked_items();

            // Ensure that no more than 2 assets are selected
            if (selected_assets.length === 0) {
                frappe.msgprint(__('Please select at least one asset to create sub-units for.'));
                return;
            }
            if (selected_assets.length > 1) {
                frappe.msgprint(__('You can only select 1 asset at a time.'));
                return;
            }

            // Open dialog for creating multiple property sub-units
            let d = new frappe.ui.Dialog({
                title: __('Enter Property Details'),
                fields: [
                    {
                        label: 'Number of Sub Units',
                        fieldname: 'num_sub_units',
                        fieldtype: 'Int',
                        reqd: 1,
                        default: 1  // Default to 1 sub-unit
                    },
                    {
                        label: 'Name Prefix',
                        fieldname: 'sub_unit_name_prefix',
                        fieldtype: 'Data',
                        reqd: 1,
                        description: 'A prefix for the property names. A number will be appended. (e.g., Tower A 10)'
                    },
                    {
                        label: 'Size (sq ft)',
                        fieldname: 'gfa_sqft',
                        fieldtype: 'Float',
                        reqd: 1
                    },
                    {
                        label: 'Gross Rent Amount',
                        fieldname: 'gross_purchase_amount',
                        fieldtype: 'Float',
                        reqd: 1
                    },
                    {
                        label: 'Item Code',
                        fieldname: 'item_code1',
                        fieldtype: 'Data',
                        reqd: 1,
                        description: 'Enter the new item code'
                    },
                    {
                        label: 'Item Name',
                        fieldname: 'item_name1',
                        fieldtype: 'Data',
                        reqd: 1,
                        description: 'Enter the new item name'
                    },
                    {
                        fieldtype: 'Button',
                        fieldname: 'create_item',
                        label: 'Create Item',
                        click: function () {
                            // Fetch item_code1 and item_name1 without triggering full form validation
                            const item_code1 = d.get_value('item_code1');
                            const item_name1 = d.get_value('item_name1');
                    
                            if (!item_code1 || !item_name1) {
                                frappe.msgprint(__('Please enter both Item Code 1 and Item Name 1.'));
                                return;
                            }
                    
                            // Call to create a new item
                            frappe.call({
                                method: 'frappe.client.insert',
                                args: {
                                    doc: {
                                        doctype: 'Item',
                                        item_code: item_code1,
                                        item_name: item_name1,
                                        item_group: 'Rent', // Set item group
                                        stock_uom: 'Nos',   // Set stock UOM
                                        is_stock_item: 0    // Optional: Set as a non-stock item
                                    }
                                },
                                callback: function (r) {
                                    if (r.message) {
                                        frappe.msgprint(__('Item {0} created successfully!', [r.message.item_code]));
                                        // Set the newly created item in the item_code field without triggering form validation
                                        d.set_value('item_code', r.message.item_code);
                                    }
                                }
                            });
                        }
                    },
                    {
                        label: 'Item Code',
                        fieldname: 'item_code',
                        fieldtype: 'Link',
                        options: 'Item',
                        reqd: 1
                    },
                    {
                        label: 'Location',
                        fieldname: 'location',
                        fieldtype: 'Link',
                        options: 'Location',
                        reqd: 1  // Required field for asset creation
                    },
                    {
                        label: 'Available-for-use Date',
                        fieldname: 'available_for_use_date',
                        fieldtype: 'Date',
                        reqd: 1
                    },
                    {
                        label: 'Purchase Date',
                        fieldname: 'purchase_date',
                        fieldtype: 'Date',
                        reqd: 1
                    }
                ],
                primary_action_label: __('Submit'),
                primary_action(values) {
                    let created_assets = 0;

                    // Loop through the selected assets
                    selected_assets.forEach(selected_asset => {
                        // Create multiple sub-units based on num_sub_units
                        for (let i = 1; i <= values.num_sub_units; i++) {
                            let asset_name = `${values.sub_unit_name_prefix} ${i}`;  // Append number to sub-unit name

                            frappe.call({
                                method: 'frappe.client.insert',
                                args: {
                                    doc: {
                                        doctype: 'Asset',
                                        asset_name: asset_name,
                                        gfa_sqft: values.gfa_sqft,
                                        gross_purchase_amount: values.gross_purchase_amount,
                                        item_code: values.item_code,
                                        location: values.location,
                                        available_for_use_date: values.available_for_use_date,
                                        purchase_date: values.purchase_date,
                                        custom_property_type: "Land",
                                        custom_against_property: selected_asset.name // Assign selected asset ID to custom_against_property
                                    }
                                },
                                callback: function (r) {
                                    if (r.message) {
                                        created_assets += 1;
                                        // Check if all assets are created
                                        if (created_assets === values.num_sub_units * selected_assets.length) {
                                            frappe.msgprint(__('Created {0} Property Sub Units successfully!', [created_assets]));
                                            d.hide();  // Hide dialog after all are created
                                        }
                                    }
                                }
                            });
                        }
                    });
                }
            });

            d.show();
        });
    }
};
