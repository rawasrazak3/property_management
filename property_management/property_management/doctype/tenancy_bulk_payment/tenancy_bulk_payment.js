// Copyright (c) 2024, Ketan Patel and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Tenancy Bulk Payment", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Tenancy Bulk Payment', {
    // onload: function (frm) {
    //     frm.set_query('main_property', function () {
    //         return {
    //             filters: {
    //                 "multi_property_against": ["is", "set"]
    //             }
    //         };
    //     });
    // },
    refresh: function (frm) {
        // Ensure the table is cleared when the form is refreshed
        // frm.clear_table('rent_table');
    },
    get_details: function (frm) {
        console.log("clicked");
        if (!frm.doc.from_date || !frm.doc.to_date) {
            frappe.msgprint(__('Please provide both From Date and To Date.'));
            return;
        }

        // Call the server-side Python method
        frappe.call({
            method: 'property_management.property_management.doctype.tenancy_bulk_payment.tenancy_bulk_payment.fetch_outstanding_rent',
            args: {
                from_date: frm.doc.from_date,
                to_date: frm.doc.to_date
            },
            callback: function (r) {
                if (r.message) {
                    console.log("received",r);
                    // Clear the child table before adding new rows
                    frm.clear_table('rent_table');
                    const rent_data = r.message;

                    // Populate the child table with fetched data
                    rent_data.forEach(data => {
                        const row = frm.add_child('rent_table');
                        row.property = data.property;
                        row.tenant = data.tenant;
                        row.outstanding_rent = data.outstanding_amount;
                        row.schedule_date = data.schedule_date;
                        row.tenancy = data.tenancy;
                        row.tenant_schedule_id = data.tenant_schedule_id;
                        row.reference_no = data.reference_no;
                        row.payment_entry = data.payment_entry;
                        row.property_name = data.property_name;
                    });

                    // Refresh the field to display the updated child table
                    frm.refresh_field('rent_table');
                } else {
                    frappe.msgprint(__('No outstanding rent found for the given date range.'));
                }
            }
        });
    },
    main_property: function (frm) {
        if (!frm.doc.main_property) {
            frappe.msgprint(__('Please select a Main Property.'));
            return;
        }

        if (!frm.doc.from_date || !frm.doc.to_date) {
            frappe.msgprint(__('Please provide both From Date and To Date.'));
            return;
        }

        // Call server-side method to fetch outstanding rent for the selected main property
        frappe.call({
            method: 'property_management.property_management.doctype.tenancy_bulk_payment.tenancy_bulk_payment.fetch_outstanding_rent_by_property',
            args: {
                main_property: frm.doc.main_property,
                from_date: frm.doc.from_date,
                to_date: frm.doc.to_date
            },
            callback: function (r) {
                if (r.message) {
                    console.log("received", r);
                    const rent_data = r.message;

                    // Populate the child table with fetched data
                    frm.clear_table('rent_table');
                    rent_data.forEach(data => {
                        const row = frm.add_child('rent_table');
                        row.property = data.property;
                        row.tenant = data.tenant;
                        row.outstanding_rent = data.outstanding_amount;
                        row.schedule_date = data.schedule_date;
                        row.tenancy = data.tenancy;
                        row.tenant_schedule_id = data.tenant_schedule_id;
                        row.reference_no = data.reference_no;
                        row.payment_entry = data.payment_entry;
                        row.property_name = data.property_name;
                    });

                    // Refresh the field to display the updated child table
                    frm.refresh_field('rent_table');
                } else {
                    frappe.msgprint(__('No outstanding rent found for the selected Main Property and date range.'));
                }
            }
        });
    }
    
});
// frappe.ui.form.on('Tenancy Bulk Payment Details',{
//     paid: function (frm, cdt, cdn) {
//         console.log("paid");
//         const row = frappe.get_doc(cdt, cdn);

//         if (!row.reference_no) {
//             frappe.msgprint(__('Reference No. is required to mark this schedule as Paid.'));
//             row.paid = 0; // Uncheck the Paid checkbox
//             frm.refresh_field('rent_table');
//             return;
//         }

//         frappe.call({
//             method: 'frappe.client.get_value',
//             args: {
//                 doctype: 'Tenancy',
//                 filters: { name: row.tenancy },
//                 fieldname: ['asset_owner']
//             },
//             callback: function (r) {
//                 if (r.message && r.message.asset_owner === 'Supplier') {
//                     // Call backend function for payment entry and sales/purchase creation
//                     frappe.call({
//                         method: 'property_management.property_management.doctype.tenancy_bulk_payment.tenancy_bulk_payment.submit_payment_and_create_entries',
//                         args: {
//                             tenancy: row.tenancy,
//                             payment_entry: row.payment_entry
//                         },
//                         callback: function (response) {
//                             if (response.message === 'success') {
//                                 frappe.msgprint(__('Payment entry and sales/purchase entries created successfully.'));
//                                 frm.save();
//                             }
//                         }
//                     });
//                 } else {
//                     // Call backend function for submitting the payment entry only
//                     frappe.call({
//                         method: 'property_management.property_management.doctype.tenancy_bulk_payment.tenancy_bulk_payment.submit_existing_payment_entry',
//                         args: {
//                             payment_entry: row.payment_entry,
//                             tenancy: row.tenancy
//                         },
//                         callback: function (response) {
//                             if (response.message === 'success') {
//                                 frappe.msgprint(__('Payment entry submitted successfully.'));
//                                 frm.save();
//                             }
//                         }
//                     });
//                 }
//             }
//         });
//     }
// });