// Copyright (c) 2025, Ketan Patel and contributors
// For license information, please see license.txt

frappe.ui.form.on("Project Summary", {
	project(frm) {
        if (frm.doc.project) {
            frappe.call({
                method: 'property_management.property_management.doctype.project_summary.project_summary.get_project_details',
                args: {
                    project_name: frm.doc.project
                },
                callback: function(r) {
                    if (!r.message) return;

                    let data = r.message;

                    // ---- Buying Price (from main property total_asset_cost) ----
                    if (data.main_property) {
                        frm.set_value("purchase_amount", data.main_property.total_asset_cost);
                    }

                    // ---- Total Expenses ----
                    if (data.total_expenses) {
                        frm.set_value("total_expense", data.total_expenses);
                    }

                    // ---- Properties Child Table ----
                    frm.clear_table("property_splits");
                    (data.properties || []).forEach(p => {
                        let row = frm.add_child("property_splits");
                        row.property = p.property;
                        row.property_name = p.property_name;
                        row.property_status = p.status;
                        row.buying_price = p.buying_price;
                        row.selling_price = p.selling_price;
                        row.profit = p.profit;
                        
                    });
                    
                    // ---- Shareholders Child Table ----
                    frm.clear_table("shareholder_details");
                    (data.shareholders || []).forEach(s => {
                        let row = frm.add_child("shareholder_details");
                        row.shareholder = s.shareholder;
                        row.shareholder_name = s.shareholder_name;
                        row.contribution = s.contribution;
                        row.amount = s.amount;
                        row.initial_contribution = s.initial_contribution;
                        row.initial_amount = s.initial_amount;
                    });

                    frm.refresh_fields();
                }
            });
        }
    },
    onload: function(frm) {
        // Set query filter for the project field
        frm.set_query("project", function() {
            return {
                filters: {
                    "status": ["!=", "Cancelled"]  // Exclude cancelled projects
                }
            };
        });
    }
});
        