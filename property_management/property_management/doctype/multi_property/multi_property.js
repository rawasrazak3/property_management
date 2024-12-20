// Copyright (c) 2024, Ketan Patel and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Multi Property", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Multi Property', {
    property: function (frm) {
        if (frm.doc.property) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Asset',
                    name: frm.doc.property,
                },
                callback: function (r) {
                    if (r.message) {
                        let asset = r.message;
                        frm.set_value('item_code', asset.item_code);
                        frm.set_value('item_name', asset.item_name);
                        frm.set_value('qty', asset.quantity || 0);
                        frm.set_value('gross_amount', asset.gross_purchase_amount || 0);
                        frm.set_value('property_governorates', asset.location);
                        frm.set_value('property_manager', asset.property_manager);
                        frm.set_value('wilayat', asset.custom_wilayat || "");
                        frm.set_value('property_owner',asset.property_owner);
                        frm.set_value('size',asset.gfa_sqft);
                        frm.set_value('rent_type',asset.rent_type);
                        frm.set_value('property_group',asset.property_group);
                        frm.set_value('property_status',asset.property_status);
                    }
                }
            });
        }
    },

    split_quantity: function (frm) {
        if (frm.doc.split_quantity && frm.doc.gross_amount) {
            frm.set_value('unit_price', frm.doc.gross_amount / frm.doc.split_quantity);
        }
    },

    split_property: function (frm) {
        if (!frm.doc.split_quantity || !frm.doc.floor_details) {
            frappe.msgprint(__('Please fill all required fields before splitting.'));
            return;
        }

        frm.clear_table('multi_property_table');

        let prefix = frm.doc.name_prefix;
        let size_per_unit = frm.doc.qty / frm.doc.split_quantity;
        let row_number = 1;

        function getFloorNumber(floorNoString) {
            if (floorNoString.toLowerCase() === "ground floor") {
                return 0; // Assign 0 for the ground floor
            }
            let match = floorNoString.match(/\d+/); // Extract numeric part
            return match ? parseInt(match[0], 10) : 0; // Default to 0 if no number is found
        }

        // Loop through floor_details to populate the table
        (frm.doc.floor_details || []).forEach(floor => {
            let floorNo = getFloorNumber(floor.floor_no);
            // Add resident units
            for (let i = 1; i <= (floor.total_resident_unit || 0); i++) {
                if (row_number > frm.doc.split_quantity) break;

                let child_row = frm.add_child('multi_property_table');
                // child_row.name_prefix = `${prefix}-${String(row_number).padStart(3, '0')}`;
                child_row.size = frm.doc.size;
                child_row.gross_amount = frm.doc.unit_price;
                child_row.item_code = `${frm.doc.item_code}-${String(floor.floor_no).padStart(2, '0')}-R${floorNo}${String(i).padStart(1)}`;
                child_row.item_name = `${frm.doc.item_code}-${String(floor.floor_no).padStart(2, '0')}-R${floorNo}${String(i).padStart(1)}`;
                child_row.floor_no = floor.floor_no;
                child_row.unit_type = 'Resident';
                child_row.property_category = 'Residential';
                child_row.property_manager = frm.doc.property_manager;
                child_row.rent_type = frm.doc.rent_type;
                child_row.property_group = frm.doc.property_group;
                child_row.property_status = frm.doc.property_status;
                child_row.available_for_use_date = frm.doc.available_for_use_date;

                row_number++;
            }

            // Add commercial units
            for (let i = 1; i <= (floor.total_commercial_unit || 0); i++) {
                if (row_number > frm.doc.split_quantity) break;

                let child_row = frm.add_child('multi_property_table');
                // child_row.name_prefix = `${prefix}-${String(row_number).padStart(3, '0')}`;
                child_row.size = frm.doc.size;
                child_row.gross_amount = frm.doc.unit_price;
                child_row.item_code = `${frm.doc.item_code}-${String(floor.floor_no).padStart(2, '0')}-C${floorNo}${String(i).padStart(1)}`;
                child_row.item_name = `${frm.doc.item_code}-${String(floor.floor_no).padStart(2, '0')}-C${floorNo}${String(i).padStart(1)}`;
                child_row.floor_no = floor.floor_no;
                child_row.unit_type = 'Commercial';
                child_row.property_category = 'Commercial';
                child_row.property_manager = frm.doc.property_manager;
                child_row.rent_type = frm.doc.rent_type;
                child_row.property_group = frm.doc.property_group;

                row_number++;
            }
        });

        frm.refresh_field('multi_property_table');
        frappe.msgprint(__('Property split successfully based on floor details.'));
    },

    // New functionality: clear and reinitialize floor details based on `no_of_floors`
    no_of_floors: function (frm) {
        if (frm.doc.no_of_floors) {
            frm.clear_table('floor_details');
            for (let i = 0; i <= frm.doc.no_of_floors; i++) {
                frm.add_child('floor_details', {
                    floor_no: i === 0 ? 'Ground Floor' : `Floor No-${i}`,
                    total_resident_unit: 0,
                    total_commercial_unit: 0,
                });
            }
            frm.refresh_field('floor_details');
        }
    },
});
