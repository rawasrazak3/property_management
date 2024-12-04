// Copyright (c) 2024, Ketan Patel and contributors
// For license information, please see license.txt

frappe.ui.form.on("Rent Item", {
	onload(frm) {
        frm.set_query('item_group', function() {
            return {
                filters: {
                    parent_item_group: "PROPERTY RENTAL MASTER"
                }
            };
        });

	},
});
