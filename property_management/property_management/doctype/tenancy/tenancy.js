// Copyright (c) 2024, Ketan Patel and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tenancy", {
    refresh: function(frm, cdt, cdn) {
    	// if (frm.doc.docstatus != 1) {
	        frm.add_custom_button(__("Get Schedule"), function() {
	            frm.clear_table("tenant_schedule");
	            frappe.call({
	                method: "frappe.client.get",
	                args: {
	                    doctype: "Asset Depreciation Schedule",
	                filters: {
	                	"asset": cur_frm.doc.asset
	                },
	                fieldname:["asset"]
	                },	               
	                callback(r) {
	                    if (r.message) {
	                        for (var row in r.message.depreciation_schedule) {
	                            var child = frm.add_child("tenant_schedule");
	                            var rms = r.message.depreciation_schedule[row];
	                            frappe.model.set_value(child.doctype, child.name, "schedule_date", rms.schedule_date);
	                            frappe.model.set_value(child.doctype, child.name, "tenant_schedule_id", rms.name);
	                            frappe.model.set_value(child.doctype, child.name, "amount", rms.depreciation_amount);
	                            frappe.model.set_value(child.doctype, child.name, "total_amount", rms.accumulated_depreciation_amount);
	                            frm.refresh_field("tenant_schedule");
	                        }
	                    }
	                }
	            });
	        });
		// }
    }
});

frappe.ui.form.on('Tenancy', {
	refresh: function(frm) {
		frm.fields_dict.tenant_schedule.grid.wrapper.find('.grid-remove-rows').hide();
		frm.fields_dict.tenant_schedule.grid.wrapper.find('.grid-add-row').hide();
	}
});

frappe.ui.form.on('Tenant Schedule', {
	form_render(frm, cdt, cdn) {
        frm.fields_dict.tenant_schedule.grid.wrapper.find('.grid-delete-row').hide();
        frm.fields_dict.tenant_schedule.grid.wrapper.find('.grid-duplicate-row').hide();
        frm.fields_dict.tenant_schedule.grid.wrapper.find('.grid-move-row').hide();
        frm.fields_dict.tenant_schedule.grid.wrapper.find('.grid-append-row').hide();
        frm.fields_dict.tenant_schedule.grid.wrapper.find('.grid-insert-row-below').hide();
        frm.fields_dict.tenant_schedule.grid.wrapper.find('.grid-insert-row').hide();
    }
});

frappe.ui.form.on('Tenant Schedule', {
	invoice: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		// frappe.model.set_value(cdt,cdn,'pending_amount', d.amount - d.invoice_amount);
	},
	is_invoice: function(frm, cdt, cdn) {
    var e = locals[cdt][cdn];
    
    // Check if invoice is flagged
    if (e.is_invoice == 1) {
        if (frm.doc.is_tenant_tenancy == 1) {
            // Create invoice for tenant tenancy
            createInvoice(frm, cdt, cdn);
        } else if (frm.doc.is_landlord_tenancy == 1) {
            // Create invoice for landlord tenancy
            createInvoicelandlord(frm, cdt, cdn);
        }
    }
}

});

// frappe.ui.form.on('Tenant Schedule', {
// 	is_paid: function(frm,cdt,cdn) {
// 		var e = locals[cdt][cdn];
// 		if (frm.doc.is_tenant_tenancy == 1){
// 			if(e.is_paid == 1){
// 				create_paymententry(frm,cdt,cdn);
// 			}
// 		} else if(frm.doc.is_landlord_tenancy == 1){
// 			if(e.is_paid == 1){
// 				create_paymententry_landlord(frm,cdt,cdn);
// 			}
// 		}
// 	}
// });

function createInvoice(frm,cdt,cdn) {
	var row = locals[cdt][cdn];
    frappe.call({
        method: 'property_management.property_management.doctype.tenancy.tenancy.create_invoice',
        args: {
            tenant: frm.doc.tenant,
            prt: frm.doc.asset,
            prt_name: frm.doc.asset_name,
            amt: row.amount,
            custom_tenancy_id: frm.doc.name
        },
        callback: function(response) {
            if (response.message) {
                frappe.model.set_value(cdt,cdn,'invoice', response.message);
                frm.save('Update');
                // frappe.msgprint(`${response.message} Invoice created successfully!`);
            } else {
                frappe.msgprint('Failed to create invoice');
            }
        }
    });
}
// frappe.ui.form.on('Tenancy', {
//     refresh: function(frm) {
//         // Add a custom button called "Create Invoice"
//         frm.add_custom_button(__('Create Invoice'), function() {
//             // Disable the button to prevent multiple submissions
//             frm.disable_save();

//             let promises = [];

//             // Iterate over the tenant_schedule child table rows
//             frm.doc.tenant_schedule.forEach(function(row) {
//                 if (!row.is_invoice) { // Only process rows without an invoice
//                     promises.push(new Promise((resolve, reject) => {
//                         frappe.call({
//                             method: 'property_management.property_management.doctype.tenancy.tenancy.create_invoice',
//                             args: {
//                                 tenant: frm.doc.tenant,
//                                 prt: frm.doc.asset,
//                                 prt_name: frm.doc.asset_name,
//                                 amt: row.amount,
//                                 custom_tenancy_id: frm.doc.name
//                             },
//                             callback: function(response) {
//                                 if (response.message) {
//                                     // Set the invoice number in the row
//                                     frappe.model.set_value(row.doctype, row.name, 'invoice', response.message);
//                                     frappe.model.set_value(row.doctype, row.name, 'is_invoice', 1);
//                                     resolve();
//                                 } else {
//                                     reject('Failed to create invoice');
//                                 }
//                             }
//                         });
//                     }));
//                 }
//             });

//             // Wait for all invoices to be created
//             Promise.all(promises).then(() => {
//                 // Refresh the field to reflect changes
//                 frm.refresh_field('tenant_schedule');
//                 // Save the form after making the changes
//                 frm.save_or_update();
//             }).catch((error) => {
//                 frappe.msgprint(error);
//             }).finally(() => {
//                 // Re-enable the save button
//                 frm.enable_save();
//             });
//         });
//     }
// });


function createInvoicelandlord(frm,cdt,cdn) {
	var row = locals[cdt][cdn];
    frappe.call({
        method: 'property_management.property_management.doctype.tenancy.tenancy.create_invoice_landlord',
        args: {
            landlord: frm.doc.landlord,
            prt: frm.doc.asset,
            prt_name: frm.doc.asset_name,
            amt: row.amount,
            custom_tenancy_id: frm.doc.name
        },
        callback: function(response) {
            if (response.message) {
                frappe.model.set_value(cdt,cdn,'invoice', response.message);
                frm.save('Update');
                // frappe.msgprint(`${response.message} Invoice created successfully!`);
            } else {
                frappe.msgprint('Failed to create invoice');
            }
        }
    });
}

// function create_paymententry(frm,cdt,cdn) {
// 	var row = locals[cdt][cdn];
// 	invoice_name = row.invoice
// 	payment_amount = row.invoice_amount
// 	schedule_date = row.schedule_date
// 	console.log(":::::::::::::::::::::::::::::::::::::::::",row)
//     frappe.call({
//         method: 'property_management.property_management.doctype.tenancy.tenancy.create_paymententry',
//         args: {
//             party: frm.doc.tenant,
//             payment_amount: row.invoice_amount,
//             paid_amount: row.invoice_amount,
//             received_amount: row.invoice_amount,
//             paid_to: row.paid_to,
//             invoice_name: row.invoice,
//             doc: frm.doc.name,
//             schedule_date: schedule_date,
//             invoice_ref: row.invoice
//         },
//         callback: function(response) {
//             if (response.message) {
//                 // frappe.msgprint(`${response.message} Payment Entry created successfully!`);
//                 frappe.model.set_value(cdt,cdn,'payment_entry', response.message);
//                 frm.save('Update');
//             } else {
//                 frappe.msgprint('Failed to create payment entry');
//             }
//         }
//     });
// }

// function create_paymententry(frm, cdt, cdn) {
//     var row = locals[cdt][cdn];
//     var invoice_name = row.invoice;
//     var payment_amount = row.invoice_amount;
//     var schedule_date = row.schedule_date;

//     console.log(":::::::::::::::::::::::::::::::::::::::::", row.invoice);

//     // Fetch default bank account
//     frappe.call({
//         method: 'frappe.client.get_value',
//         args: {
//             doctype: 'Company',
//             fieldname: 'default_cash_account',
//             filters: {
//                 name: frm.doc.company // assuming you have the company in the form
//             }
//         },
//         callback: function(r) {
//             if (r && r.message) {
//                 var default_cash_account = r.message.default_cash_account;

//                 // Proceed with creating the payment entry using the default bank account
//                 frappe.call({
//                     method: 'property_management.property_management.doctype.tenancy.tenancy.create_paymententry',
//                     args: {
//                         party: frm.doc.tenant,
//                         payment_amount: row.invoice_amount,
//                         paid_amount: row.invoice_amount,
//                         reference_no: row.reference_no,
//                         received_amount: row.invoice_amount,
//                         paid_to: default_cash_account, // set default bank account here
//                         invoice_name: row.invoice,
//                         doc: frm.doc.name,
//                         schedule_date: schedule_date,
//                         posting_date: schedule_date,
//                         invoice_ref: row.invoice
//                     },
//                     callback: function(response) {
//                         if (response.message) {
//                             frappe.model.set_value(cdt, cdn, 'payment_entry', response.message);
//                             frm.save('Update');
//                         } else {
//                             frappe.msgprint('Failed to create payment entry');
//                         }
//                     }
//                 });
//             } else {
//                 frappe.msgprint('Failed to fetch default bank account');
//             }
//         }
//     });
// }



// function create_paymententry_landlord(frm,cdt,cdn) {
// 	var row = locals[cdt][cdn];
// 	invoice_name = row.invoice
// 	payment_amount = row.invoice_amount
// 	schedule_date = row.schedule_date
// 	console.log(":::::::::::::::::::::::::::::::::::::::::",row.paid_to)
//     frappe.call({
//         method: 'property_management.property_management.doctype.tenancy.tenancy.create_paymententry_landlord',
//         args: {
//             party: frm.doc.landlord,
//             payment_amount: row.invoice_amount,
//             paid_amount: row.invoice_amount,
//             received_amount: row.invoice_amount,
//             paid_to: row.paid_to,
//             invoice_name: row.invoice,
//             doc: frm.doc.name,
//             schedule_date: schedule_date,
//             invoice_ref: row.invoice
//         },
//         callback: function(response) {
//             if (response.message) {
//                 // frappe.msgprint(`${response.message} Payment Entry created successfully!`);
//                 frappe.model.set_value(cdt,cdn,'payment_entry', response.message);
//                 frm.save('Update');
//             } else {
//                 frappe.msgprint('Failed to create payment entry');
//             }
//         }
//     });
// }

function create_paymententry_landlord(frm, cdt, cdn) {
    var row = locals[cdt][cdn];
    var invoice_name = row.invoice;
    var payment_amount = row.invoice_amount;
    var schedule_date = row.schedule_date;

    console.log(":::::::::::::::::::::::::::::::::::::::::", row.paid_to);

    // Fetch default cash account
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: 'Company',
            fieldname: 'default_cash_account',
            filters: {
                name: frm.doc.company // assuming you have the company in the form
            }
        },
        callback: function(r) {
            if (r && r.message) {
                var default_cash_account = r.message.default_cash_account;

                // Proceed with creating the payment entry using the default cash account
                frappe.call({
                    method: 'property_management.property_management.doctype.tenancy.tenancy.create_paymententry_landlord',
                    args: {
                        party: frm.doc.landlord,
                        payment_amount: row.invoice_amount,
                        paid_amount: row.invoice_amount,
                        received_amount: row.invoice_amount,
                        paid_to: default_cash_account, // set default cash account here
                        invoice_name: row.invoice,
                        doc: frm.doc.name,
                        posting_date : schedule_date,
                        schedule_date: schedule_date,
                        invoice_ref: row.invoice
                    },
                    callback: function(response) {
                        if (response.message) {
                            frappe.model.set_value(cdt, cdn, 'payment_entry', response.message);
                            frm.save('Update');
                        } else {
                            frappe.msgprint('Failed to create payment entry');
                        }
                    }
                });
            } else {
                frappe.msgprint('Failed to fetch default cash account');
            }
        }
    });
}


frappe.ui.form.on('Tenancy', {
	is_tenant_tenancy: function(frm) {
		if (frm.doc.is_tenant_tenancy == 1) {
			frm.set_value('naming_series', "TT.-");
			frm.set_value('is_landlord_tenancy', 0);
			frm.set_value('landlord', undefined);
		}
	},
	is_landlord_tenancy: function(frm) {
		if (frm.doc.is_landlord_tenancy == 1) {
			frm.set_value('naming_series', "LT.-");
			frm.set_value('is_tenant_tenancy', 0);
			frm.set_value('tenant', undefined);
		}
	}
});

frappe.ui.form.on('Tenancy', {
	validate: function(frm) {
		if (frm.doc.is_tenant_tenancy == 0 && frm.doc.is_landlord_tenancy == 0) {
			frappe.msgprint({
			    title: __('Error'),
			    indicator: 'red',
			    message: __('Please select one of the <b>Is Tenant Tenancy</b> or <b>Is Landlord Tenancy</b>')
			});
			validated = false;
		}
	}
});

frappe.ui.form.on("Tenancy", "refresh", function(frm) {
	frm.set_query("asset", function() {
		return {
			"filters": {
				"docstatus": 1
			}
        };
    }),
	frm.set_query("tenant", function() {
		return {
			"filters": {
				"is_tenant": 1
			}
        };
    }),
    frm.set_query("landlord", function() {
		return {
			"filters": {
				"is_landlord": 1
			}
        };
    });
});

// frappe.ui.form.on('Tenancy', {
//     refresh: function(frm) {
//         // Add a custom button called "Create Invoice"
//         frm.add_custom_button(__('Create Invoice'), function() {
//             // Iterate over the tenant_schedule child table rows
//             frm.doc.tenant_schedule.forEach(function(row) {
//                 // Set the 'is_invoice' checkbox to 1 (checked) for each row
//                 frappe.model.set_value(row.doctype, row.name, 'is_invoice', 1);
//             });

//         });
//     }
// });

frappe.ui.form.on('Tenant Schedule', {
    is_purchase: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];

        // Proceed only if asset_owner is 'Supplier'
        if (frm.doc.asset_owner === 'Supplier' && row.is_purchase == 1) {
            createPurchaseInvoice(frm, cdt, cdn);
        }
    },
    is_purchase_payment: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];

        // Proceed only if asset_owner is 'Supplier'
        if (frm.doc.asset_owner === 'Supplier' && row.is_purchase_payment == 1) {
            createPurchasePaymentEntry(frm, cdt, cdn);
        }
    }
});

// function createPurchaseInvoice(frm, cdt, cdn) {
//     var row = locals[cdt][cdn];
//     var commission = frm.doc.commission || 0; // Default commission to 0 if not defined
//     var commission_amount = (commission / 100) * row.invoice_amount;
//     var net_amount = row.invoice_amount - commission_amount;

//     frappe.call({
//         method: 'property_management.property_management.doctype.tenancy.tenancy.create_purchase_invoice',
//         args: {
//             supplier: frm.doc.supplier,
//             prt: frm.doc.asset,
//             prt_name: frm.doc.asset_name,
//             net_amount: net_amount,
//             custom_tenancy_id: frm.doc.name
//         },
//         callback: function(response) {
//             if (response.message) {
//                 frappe.model.set_value(cdt, cdn, 'purchase_invoice', response.message);
//                 frm.save('Update');
//             } else {
//                 frappe.msgprint('Failed to create purchase invoice');
//             }
//         }
//     });
// }

// function createPurchasePaymentEntry(frm, cdt, cdn) {
//     var row = locals[cdt][cdn];
//     var schedule_date = row.schedule_date;

//     frappe.call({
//         method: 'frappe.client.get_value',
//         args: {
//             doctype: 'Company',
//             fieldname: 'default_cash_account',
//             filters: {
//                 name: frm.doc.company
//             }
//         },
//         callback: function(r) {
//             if (r && r.message) {
//                 var default_cash_account = r.message.default_cash_account;

//                 // Create the payment entry for purchase invoice
//                 frappe.call({
//                     method: 'property_management.property_management.doctype.tenancy.tenancy.create_purchase_payment_entry',
//                     args: {
//                         supplier: frm.doc.supplier,
//                         payment_amount: row.invoice_amount,
//                         paid_from: default_cash_account, // Added paid_to for purchase invoice
//                         purchase_invoice: row.purchase_invoice,
//                         posting_date : schedule_date,
//                         schedule_date: schedule_date,
//                         reference_no: row.reference_no,
//                         invoice_ref: row.purchase_invoice,
//                         doc: frm.doc.name
//                     },
//                     callback: function(response) {
//                         if (response.message) {
//                             frappe.model.set_value(cdt, cdn, 'payment_entry_purchase', response.message);
//                             frm.save('Update');
//                         } else {
//                             frappe.msgprint('Failed to create payment entry');
//                         }
//                     }
//                 });
//             } else {
//                 frappe.msgprint('Failed to fetch default bank account');
//             }
//         }
//     });
// }

//////////////////////////////

// frappe.ui.form.on('Tenant Schedule', {
//     is_paid: function(frm, cdt, cdn) {
//         var e = locals[cdt][cdn];

//         // Check if reference_no is empty
//         if (!e.reference_no) {
//             frappe.msgprint(__('Please add a reference number before marking as paid.'));
//             frappe.model.set_value(cdt, cdn, 'is_paid', 0);  // Uncheck the 'is_paid' checkbox
//             return;  // Stop further execution
//         }

//         // Check if is_paid is 1 and the asset owner is Supplier
//         if (e.is_paid == 1) {
//             if (frm.doc.asset_owner == "Supplier") {
//                 console.log("Asset owner is Supplier, proceeding with payment and purchase creation...");
//                 // Trigger the 3 actions: sales invoice payment, purchase invoice creation, and purchase payment entry creation
//                 create_sales_payment_and_purchase(frm, cdt, cdn);
//             } else {
//                 // Asset owner is not Supplier, just create sales payment entry
//                 console.log("Asset owner is not Supplier, only creating sales payment entry.");
//                 create_paymententry(frm, cdt, cdn);
//             }
//         } else {
//             console.log("is_paid is not checked, skipping payment creation.");
//         }
//     }
// });


// function create_sales_payment_and_purchase(frm, cdt, cdn) {
//     var row = locals[cdt][cdn];

//     // Step 1: Create Payment Entry for Sales Invoice
//     console.log("Creating payment entry for sales invoice...");
//     create_paymententry(frm, cdt, cdn, function() {
//         console.log("Payment entry for sales invoice created. Proceeding with purchase invoice creation...");

//         // Step 2: Check is_purchase checkbox and create Purchase Invoice
//         // frappe.model.set_value(cdt, cdn, 'is_purchase', 1); // Check the is_purchase checkbox
//         frm.save();  // Save form after checking is_purchase

//         createPurchaseInvoice(frm, cdt, cdn, function(purchase_invoice_id) {
//             // Set purchase invoice ID
//             console.log("Purchase invoice created with ID:", purchase_invoice_id);
//             frappe.model.set_value(cdt, cdn, 'purchase_invoice', purchase_invoice_id);
//             frm.save('Update');

//             // Step 3: Check is_purchase_payment checkbox and create Payment Entry for Purchase Invoice
//             // frappe.model.set_value(cdt, cdn, 'is_purchase_payment', 1); // Check the is_purchase_payment checkbox
//             frm.save();  // Save form after checking is_purchase_payment

//             console.log("Creating payment entry for purchase invoice...");
//             createPurchasePaymentEntry(frm, cdt, cdn, purchase_invoice_id);
//         });
//     });
// }

// function create_paymententry(frm, cdt, cdn, callback) {
//     var row = locals[cdt][cdn];
//     var invoice_name = row.invoice;
//     var payment_amount = row.invoice_amount;
//     var schedule_date = row.schedule_date;

//     // Fetch default bank account (paid_to)
//     frappe.call({
//         method: 'frappe.client.get_value',
//         args: {
//             doctype: 'Company',
//             fieldname: 'default_cash_account',
//             filters: {
//                 name: frm.doc.company
//             }
//         },
//         callback: function(r) {
//             if (r && r.message) {
//                 var default_cash_account = r.message.default_cash_account;

//                 // Create the payment entry
//                 frappe.call({
//                     method: 'property_management.property_management.doctype.tenancy.tenancy.create_paymententry',
//                     args: {
//                         party: frm.doc.tenant,
//                         payment_amount: row.invoice_amount,
//                         paid_amount: row.invoice_amount,
//                         reference_no: row.reference_no,
//                         received_amount: row.invoice_amount,
//                         paid_to: default_cash_account,
//                         invoice_name: row.invoice,
//                         doc: frm.doc.name,
//                         schedule_date: schedule_date,
//                         posting_date: schedule_date,
//                         invoice_ref: row.invoice
//                     },
//                     callback: function(response) {
//                         if (response.message) {
//                             frappe.model.set_value(cdt, cdn, 'payment_entry', response.message);
//                             frm.save('Update');
//                             console.log("Payment entry for sales invoice created:", response.message);

//                             if (callback) callback(); // Call the next step
//                         } else {
//                             frappe.msgprint('Failed to create payment entry for sales invoice');
//                         }
//                     }
//                 });
//             } else {
//                 frappe.msgprint('Failed to fetch default cash account');
//             }
//         }
//     });
// }

frappe.ui.form.on('Tenant Schedule', {
    is_paid: function(frm, cdt, cdn) {
        var e = locals[cdt][cdn];

        // Check if reference_no is empty
        if (!e.reference_no) {
            frappe.msgprint(__('Please add a reference number before marking as paid.'));
            frappe.model.set_value(cdt, cdn, 'is_paid', 0);  // Uncheck the 'is_paid' checkbox only in case of error
            return;  // Stop further execution
        }

        // Proceed if reference_no exists
        if (e.is_paid == 1) {
            // Check if asset owner is Supplier
            if (frm.doc.asset_owner == "Supplier") {
                console.log("Asset owner is Supplier, proceeding with payment and purchase creation...");
                
                // Submit the existing payment entry
                submit_existing_payment_entry(frm, cdt, cdn, function() {
                    // After submitting, create purchase invoice and purchase payment entry
                    create_sales_payment_and_purchase(frm, cdt, cdn, function() {
                        // Lock the is_paid checkbox after successful operation
                        frappe.model.set_value(cdt, cdn, 'is_paid', 1);  // Ensure it's checked
                        cur_frm.fields_dict['items'].grid.grid_rows_by_docname[cdn].toggle_editable('is_paid', false);  // Disable the field
                        frm.save();  // Save the form after processing
                    });
                });

            } else {
                // For non-Supplier, only submit the sales payment entry
                console.log("Asset owner is not Supplier, only submitting the sales payment entry.");
                
                submit_existing_payment_entry(frm, cdt, cdn, function() {
                    // Lock the is_paid checkbox after successful operation
                    frappe.model.set_value(cdt, cdn, 'is_paid', 1);  // Ensure it's checked
                    cur_frm.fields_dict['items'].grid.grid_rows_by_docname[cdn].toggle_editable('is_paid', false);  // Disable the field
                    frm.save();  // Save the form after processing
                });
            }
        }
    }
});



// Function to submit the existing payment entry
function submit_existing_payment_entry(frm, cdt, cdn, callback) {
    var row = locals[cdt][cdn];
    
    if (row.payment_entry) {
        // Refresh the Payment Entry document to ensure there are no conflicts
        frappe.call({
            method: 'frappe.client.get',
            args: {
                doctype: 'Payment Entry',
                name: row.payment_entry
            },
            callback: function(r) {
                if (r && r.message) {
                    // Submit the payment entry after refreshing the document
                    frappe.call({
                        method: 'frappe.client.submit',
                        args: {
                            doc: r.message  // Submitting the latest version of the Payment Entry document
                        },
                        callback: function(response) {
                            if (response.message) {
                                frappe.msgprint(`Payment entry ${row.payment_entry} submitted successfully.`);
                                if (callback) callback();  // Proceed to the next step if a callback is provided
                            } else {
                                frappe.msgprint('Failed to submit the payment entry.');
                            }
                        }
                    });
                }
            }
        });
    } else {
        frappe.msgprint('No existing payment entry found to submit.');
    }
}

function create_sales_payment_and_purchase(frm, cdt, cdn) {
    var row = locals[cdt][cdn];

    // Step 2: Create Purchase Invoice
    createPurchaseInvoice(frm, cdt, cdn, function(purchase_invoice_id) {
        // Set purchase invoice ID
        frappe.model.set_value(cdt, cdn, 'purchase_invoice', purchase_invoice_id);
        frm.save('Update');

        // Step 3: Create Payment Entry for Purchase Invoice
        // createPurchasePaymentEntry(frm, cdt, cdn, purchase_invoice_id);

        //Create Sales Invoice With Commission
        createSalesInvoiceWithCommission(frm, cdt, cdn, function(invoice_id) {
            frappe.model.set_value(cdt, cdn, 'sales_invoice_commission', invoice_id);
            frm.save('Update'); // Save the form after setting the values
        });
    });
}

function createPurchaseInvoice(frm, cdt, cdn, callback) {
    var row = locals[cdt][cdn];
    var commission = frm.doc.commission || 0; // Default commission to 0 if not defined
    var one_time_commission = frm.doc.one_time_commission || 0; // Default one_time_commission to 0 if not defined
    var net_amount = row.amount;
    
    // Check the condition for 'Supplier' and 'one_time_commission'
    if (frm.doc.asset_owner === "Supplier" && one_time_commission > 0 && frm.doc.start_date === row.schedule_date) {
        // Calculate net amount based on commission + one_time_commission
        var commission_amount = ((commission + one_time_commission) / 100) * row.amount;
        net_amount = row.amount - commission_amount;
    } else {
        // Usual flow, commission only
        var commission_amount = (commission / 100) * row.amount;
        net_amount = row.amount - commission_amount;
    }

    // Create Purchase Invoice
    frappe.call({
        method: 'property_management.property_management.doctype.tenancy.tenancy.create_purchase_invoice',
        args: {
            supplier: frm.doc.supplier,
            prt: frm.doc.asset,
            prt_name: frm.doc.asset_name,
            net_amount: row.amount,
            custom_tenancy_id: frm.doc.name
        },
        callback: function(response) {
            if (response.message) {
                console.log("Purchase invoice created with ID:", response.message);
                if (callback) callback(response.message); // Pass the Purchase Invoice ID to callback
            } else {
                frappe.msgprint('Failed to create purchase invoice');
            }
        }
    });
}


function createPurchasePaymentEntry(frm, cdt, cdn, purchase_invoice) {
    var row = locals[cdt][cdn];
    var schedule_date = row.schedule_date;

    // Fetch default cash account (paid_from)
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: 'Company',
            fieldname: 'default_cash_account',
            filters: {
                name: frm.doc.company
            }
        },
        callback: function(r) {
            if (r && r.message) {
                var default_cash_account = r.message.default_cash_account;

                // Create payment entry for purchase invoice
                frappe.call({
                    method: 'property_management.property_management.doctype.tenancy.tenancy.create_purchase_payment_entry',
                    args: {
                        supplier: frm.doc.supplier,
                        payment_amount: row.amount,
                        paid_from: default_cash_account, // Paid from for Purchase Invoice
                        purchase_invoice: row.purchase_invoice,
                        posting_date: schedule_date,
                        schedule_date: schedule_date,
                        reference_no: row.reference_no,
                        invoice_ref: row.purchase_invoice,
                        doc: frm.doc.name
                    },
                    callback: function(response) {
                        if (response.message) {
                            frappe.model.set_value(cdt, cdn, 'payment_entry_purchase', response.message);
                            frm.save('Update');
                            console.log("Payment entry for purchase invoice created:", response.message);
                        } else {
                            frappe.msgprint('Failed to create payment entry for purchase invoice');
                        }
                    }
                });
            } else {
                frappe.msgprint('Failed to fetch default cash account');
            }
        }
    });
}

/////////////////////////////////

frappe.ui.form.on('Tenancy', {
    refresh: function(frm) {
        if (frm.doc.docstatus == 1) {  // Check if docstatus is 1 (submitted)
            frm.add_custom_button(__('Create Invoices'), function() {
                createInvoicesForAllRows(frm);
            });
        }
    }
});


function createInvoicesForAllRows(frm) {
    // Function to process each row asynchronously
    function processRow(index) {
        if (index < frm.doc.tenant_schedule.length) {
            let row = frm.doc.tenant_schedule[index];
            // Check if an invoice is already created
            if (!row.invoice) {
                // Create an invoice if none exists
                createInvoiceForRow(frm, row, function() {
                    // After processing this row, save and move to the next row
                    frm.save('Update').then(function() {
                        processRow(index + 1);
                    });
                });
            } else {
                // Move to the next row if invoice already exists
                processRow(index + 1);
            }
        }
    }

    // Start processing from the first row
    processRow(0);
}

function createInvoiceForRow(frm, row, callback) {
    frappe.call({
        method: 'property_management.property_management.doctype.tenancy.tenancy.create_invoice',
        args: {
            tenant: frm.doc.tenant,
            prt: frm.doc.asset,
            prt_name: frm.doc.asset_name,
            amt: row.amount,
            custom_tenancy_id: frm.doc.name
        },
        callback: function(response) {
            if (response.message) {
                // Set the invoice ID in the row and execute the callback
                frappe.model.set_value(row.doctype, row.name, 'invoice', response.message);
                frappe.msgprint(`Invoice ${response.message} created successfully for ${row.amount}!`);
                callback();
            } else {
                frappe.msgprint('Failed to create invoice');
                callback(); // Continue processing the next row even if invoice creation fails
            }
        }
    });
}
/////////////////////////////////////

frappe.ui.form.on('Tenancy', {
    refresh: function(frm) {
        if (frm.doc.docstatus == 1) {  // Check if docstatus is 1 (submitted)
            frm.add_custom_button(__('Create Payment Entries'), function() {
                createPaymentEntriesForAllRows(frm);
            });
        }
    }
});

function createPaymentEntriesForAllRows(frm) {
    // Function to process each row asynchronously
    function processRow(index) {
        if (index < frm.doc.tenant_schedule.length) {
            let row = frm.doc.tenant_schedule[index];
            
            // Check if reference_no is missing
            if (!row.reference_no) {
                frappe.msgprint(`Reference No. is missing for the row with Schedule Date ${row.schedule_date}. Please add it to proceed.`);
                processRow(index + 1);  // Move to the next row
                return;  // Skip the current row
            }

            // Check if a payment entry is already created and invoice exists
            if (!row.payment_entry && row.invoice) {
                // Create a payment entry if none exists for the row
                createPaymentEntryForRow(frm, row, function() {
                    // After processing this row, save and move to the next row
                    frm.save('Update').then(function() {
                        processRow(index + 1);
                    });
                });
            } else {
                // Move to the next row if payment entry already exists or invoice is missing
                processRow(index + 1);
            }
        }
    }

    // Start processing from the first row
    processRow(0);
}


function createPaymentEntryForRow(frm, row, callback) {
    // Fetch default bank account (paid_to)
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: 'Company',
            fieldname: 'default_cash_account',
            filters: {
                name: frm.doc.company
            }
        },
        callback: function(r) {
            if (r && r.message) {
                var default_cash_account = r.message.default_cash_account;

                // Create the payment entry
                frappe.call({
                    method: 'property_management.property_management.doctype.tenancy.tenancy.create_paymententry', // Replace with your method
                    args: {
                        party: frm.doc.tenant,
                        payment_amount: row.invoice_amount,
                        paid_amount: row.invoice_amount,
                        reference_no: row.reference_no,
                        received_amount: row.invoice_amount,
                        mode_of_payment: row.mode_of_payment,
                        paid_to: row.is_paid_account, // Use Mode of Payment account as 'paid_to'
                        invoice_name: row.invoice,
                        doc: frm.doc.name,
                        schedule_date: row.schedule_date,
                        posting_date: row.schedule_date,
                        invoice_ref: row.invoice
                    },
                    callback: function(response) {
                        if (response.message) {
                            // Set the payment entry ID in the row and execute the callback
                            frappe.model.set_value(row.doctype, row.name, 'payment_entry', response.message);
                            frappe.msgprint(`Payment entry ${response.message} created successfully for ${row.invoice_amount}!`);
                            callback();
                        } else {
                            frappe.msgprint('Failed to create payment entry');
                            callback(); // Continue processing the next row even if payment entry creation fails
                        }
                    }
                });
            } else {
                frappe.msgprint('Failed to fetch Mode of Payment account');
                callback(); // Continue processing if account fetch fails
            }
        }
    });
}

frappe.ui.form.on('Tenant Schedule', {
    mode_of_payment: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];

        if (row.mode_of_payment) {
            // Fetch the account based on the mode of payment via custom method
            frappe.call({
                method: 'property_management.property_management.doctype.tenancy.tenancy.get_default_account', // Update with correct path
                args: {
                    mode_of_payment: row.mode_of_payment
                },
                callback: function(r) {
                    if (r.message) {
                        // Set the fetched account in the is_paid_account field
                        frappe.model.set_value(cdt, cdn, 'is_paid_account', r.message);
                    } else {
                        frappe.msgprint(__('No account found for the selected mode of payment'));
                    }
                }
            });
        }
    }
});




////////////////////////////////////////////////

frappe.ui.form.on('Tenant Schedule', {
    partial_payment: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        var partial_paid_amount = row.partial_paid_amount;

        // Ensure partial amount is entered
        if (!partial_paid_amount || partial_paid_amount <= 0) {
            frappe.msgprint(__('Please enter a valid partial payment amount.'));
            return;
        }

        // Check for existing payment entries and assign accordingly
        if (!row.payment_entry_1) {
            // First partial payment
            create_partial_paymententry(frm, cdt, cdn, 'payment_entry_1', 'paid_amount_1', 'outstanding_1', partial_paid_amount, function() {
                // Save the document after updating payment_entry_1
                frm.save('Update');
            });

            if (frm.doc.asset_owner == "Supplier") {
                console.log("Asset owner is Supplier, proceeding with payment and purchase creation...");
                
                // After submitting, create purchase invoice and purchase payment entry
                create_sales_payment_and_purchase(frm, cdt, cdn, function() {
                    // Optionally save again if additional changes are made
                    // frm.save();
                });
            }

        } else if (!row.payment_entry_2) {
            // Second partial payment
            create_partial_paymententry(frm, cdt, cdn, 'payment_entry_2', 'paid_amount_2', 'outstanding_2', partial_paid_amount, function() {
                frm.save();
            });
        } else if (!row.payment_entry_3) {
            // Third partial payment
            create_partial_paymententry(frm, cdt, cdn, 'payment_entry_3', 'paid_amount_3', 'outstanding_3', partial_paid_amount, function() {
                frm.save();
            });
        } else if (!row.payment_entry_4) {
            // Fourth partial payment
            create_partial_paymententry(frm, cdt, cdn, 'payment_entry_4', 'paid_amount_4', 'outstanding_4', partial_paid_amount, function() {
                frm.save();
            });
        } else {
            frappe.msgprint(__('All four partial payments have already been made.'));
        }
    }
});

// Create partial payment entry and update fields
function create_partial_paymententry(frm, cdt, cdn, payment_entry_field, paid_amount_field, outstanding_field, partial_paid_amount) {
    var row = locals[cdt][cdn];
    var invoice_name = row.invoice;
    var schedule_date = row.schedule_date;

    // Fetch default bank account (paid_to)
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: 'Company',
            fieldname: 'default_cash_account',
            filters: {
                name: frm.doc.company
            }
        },
        callback: function(r) {
            if (r && r.message) {
                var default_cash_account = r.message.default_cash_account;

                // Create the payment entry for the partial amount
                frappe.call({
                    method: 'property_management.property_management.doctype.tenancy.tenancy.create_partial_paymententry',
                    args: {
                        party: frm.doc.tenant,
                        payment_amount: partial_paid_amount,
                        paid_amount: partial_paid_amount,
                        reference_no: row.reference_no,
                        received_amount: partial_paid_amount,
                        paid_to: default_cash_account,
                        invoice_name: row.invoice,
                        doc: frm.doc.name,
                        schedule_date: schedule_date,
                        posting_date: schedule_date,
                        invoice_ref: row.invoice
                    },
                    callback: function(response) {
                        if (response.message) {
                            // Set the payment entry ID and amounts
                            frappe.model.set_value(cdt, cdn, payment_entry_field, response.message);
                            frappe.model.set_value(cdt, cdn, paid_amount_field, partial_paid_amount);

                            // Calculate outstanding amount
                            var total_amount = row.amount;
                            var previous_outstanding = row[outstanding_field.replace(/\d$/, (n) => n - 1)] || total_amount;
                            var new_outstanding = previous_outstanding - partial_paid_amount;

                            frappe.model.set_value(cdt, cdn, outstanding_field, new_outstanding);
                            frm.save('Update');
                            console.log(`Partial payment entry created: ${response.message}`);
                        } else {
                            frappe.msgprint('Failed to create partial payment entry.');
                        }
                    }
                });
            } else {
                frappe.msgprint('Failed to fetch default cash account.');
            }
        }
    });
}

///////////////////////////////////////////////

frappe.ui.form.on('Tenant Schedule', {
    is_sales_commission: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];

        // Check if the is_sales_commission checkbox is ticked
        if (row.is_sales_commission) {
            createSalesInvoiceWithCommission(frm, cdt, cdn, function(invoice_id) {
                // After creating the sales invoice, create the payment entry
                // Update the child table fields
                frappe.model.set_value(cdt, cdn, 'sales_invoice_commission', invoice_id);
                frm.save('Update'); // Save the form after setting the values
            });
        }
    }
});

function createSalesInvoiceWithCommission(frm, cdt, cdn, callback) {
    var row = locals[cdt][cdn];
    var commission_percentage = frm.doc.commission || 0;  // 3% commission
    var one_time_commission_percentage = frm.doc.one_time_commission || 0;  // 5% one-time commission
    var total_gross_rent_amount = frm.doc.total_gross_rent_amount || 0;  // e.g., 300
    var tenant_schedule_amount = row.amount || 0;  // e.g., 100
    var net_commission = 0;

    // Check if start_date equals schedule_date and asset_owner is 'Supplier'
    if (frm.doc.asset_owner === "Supplier" && frm.doc.start_date === row.schedule_date) {
        // Calculate both 3% of total_gross_rent_amount and 5% of tenant_schedule_amount
        var commission_amount = (commission_percentage / 100) * tenant_schedule_amount;  // e.g., 3% of 300
        var one_time_commission_amount = (one_time_commission_percentage / 100) * total_gross_rent_amount;  // e.g., 5% of 100
        net_commission = commission_amount + one_time_commission_amount;
    } else if (frm.doc.asset_owner === "Supplier") {
        // If dates don't match, only calculate 5% of tenant_schedule_amount
        net_commission = (commission_percentage / 100) * tenant_schedule_amount;
    }

    // Create Sales Invoice with "Commission" as the item
    frappe.call({
        method: 'property_management.property_management.doctype.tenancy.tenancy.create_sales_invoice',
        args: {
            customer: frm.doc.tenant,
            commission: net_commission,  // Use the calculated commission amount
            tenancy_id: frm.doc.name,
            child_row_name: row.name  // Pass the child row name for tracking
        },
        callback: function(response) {
            if (response.message) {
                if (callback) callback(response.message);  // Pass the sales invoice ID to callback
            } else {
                frappe.msgprint('Failed to create sales invoice for commission');
            }
        }
    });
}


function createPaymentEntryForCommission(frm, row, invoice_id, callback) {
    // Fetch default bank account (paid_to)
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: 'Company',
            fieldname: 'default_cash_account',
            filters: {
                name: frm.doc.company
            }
        },
        callback: function(r) {
            if (r && r.message) {
                var default_cash_account = r.message.default_cash_account;

                // Create the payment entry
                frappe.call({
                    method: 'property_management.property_management.doctype.tenancy.tenancy.create_paymententry', 
                    args: {
                        party: frm.doc.tenant,
                        payment_amount: row.amount, // Assuming row.amount is the invoice amount
                        paid_amount: row.amount,
                        reference_no: invoice_id,
                        received_amount: row.amount,
                        paid_to: default_cash_account,
                        invoice_name: invoice_id,
                        doc: frm.doc.name,
                        schedule_date: row.schedule_date,
                        posting_date: row.schedule_date,
                        invoice_ref: invoice_id
                    },
                    callback: function(response) {
                        if (response.message) {
                            // Set the payment entry ID in the row and execute the callback
                            callback(response.message); // Pass payment entry ID to callback
                        } else {
                            frappe.msgprint('Failed to create payment entry');
                            callback(); // Continue processing the next row even if payment entry creation fails
                        }
                    }
                });
            } else {
                frappe.msgprint('Failed to fetch default cash account');
                callback(); // Continue processing if cash account fetch fails
            }
        }
    });
}




// frappe.ui.form.on('Tenant Schedule', {
//     is_paid: function(frm, cdt, cdn) {
//         var e = locals[cdt][cdn];

//         if (e.is_paid == 1) {
//             if (frm.doc.asset_owner == "Supplier") {
//                 // Trigger the 3 actions: sales invoice payment, purchase invoice creation, and purchase payment entry creation
//                 create_sales_payment_and_purchase(frm, cdt, cdn);
//             } else {
//                 // If asset owner is not Supplier, just create payment entry for sales invoice
//                 create_paymententry(frm, cdt, cdn);
//             }
//         }
//     }
// });

// function create_sales_payment_and_purchase(frm, cdt, cdn) {
//     var row = locals[cdt][cdn];

//     // Step 1: Create Payment Entry for Sales Invoice
//     create_paymententry(frm, cdt, cdn, function() {
//         // Step 2: Create Purchase Invoice
//         createPurchaseInvoice(frm, cdt, cdn, function(purchase_invoice_id) {
//             // Set purchase invoice ID
//             frappe.model.set_value(cdt, cdn, 'purchase_invoice', purchase_invoice_id);
//             frm.save('Update');

//             // Step 3: Create Payment Entry for Purchase Invoice
//             createPurchasePaymentEntry(frm, cdt, cdn, purchase_invoice_id);
//         });
//     });
// }

// function create_paymententry(frm, cdt, cdn, callback) {
//     var row = locals[cdt][cdn];
//     var invoice_name = row.invoice;
//     var payment_amount = row.invoice_amount;
//     var schedule_date = row.schedule_date;

//     // Fetch default bank account (paid_to)
//     frappe.call({
//         method: 'frappe.client.get_value',
//         args: {
//             doctype: 'Company',
//             fieldname: 'default_cash_account',
//             filters: {
//                 name: frm.doc.company
//             }
//         },
//         callback: function(r) {
//             if (r && r.message) {
//                 var default_cash_account = r.message.default_cash_account;

//                 // Create the payment entry
//                 frappe.call({
//                     method: 'property_management.property_management.doctype.tenancy.tenancy.create_paymententry',
//                     args: {
//                         party: frm.doc.tenant,
//                         payment_amount: row.invoice_amount,
//                         paid_amount: row.invoice_amount,
//                         reference_no: row.reference_no,
//                         received_amount: row.invoice_amount,
//                         paid_to: default_cash_account,
//                         invoice_name: row.invoice,
//                         doc: frm.doc.name,
//                         schedule_date: schedule_date,
//                         posting_date: schedule_date,
//                         invoice_ref: row.invoice
//                     },
//                     callback: function(response) {
//                         if (response.message) {
//                             frappe.model.set_value(cdt, cdn, 'payment_entry', response.message);
//                             frm.save('Update');
//                             if (callback) callback();
//                         } else {
//                             frappe.msgprint('Failed to create payment entry');
//                         }
//                     }
//                 });
//             } else {
//                 frappe.msgprint('Failed to fetch default cash account');
//             }
//         }
//     });
// }

// function createPurchaseInvoice(frm, cdt, cdn, callback) {
//     var row = locals[cdt][cdn];
//     var commission = frm.doc.commission || 0; // Default commission to 0 if not defined
//     var commission_amount = (commission / 100) * row.invoice_amount;
//     var net_amount = row.invoice_amount - commission_amount;

//     frappe.call({
//         method: 'property_management.property_management.doctype.tenancy.tenancy.create_purchase_invoice',
//         args: {
//             supplier: frm.doc.supplier,
//             prt: frm.doc.asset,
//             prt_name: frm.doc.asset_name,
//             net_amount: net_amount,
//             custom_tenancy_id: frm.doc.name
//         },
//         callback: function(response) {
//             if (response.message) {
//                 frappe.msgprint('Purchase invoice created successfully: ' + response.message);
//                 if (callback) callback(response.message); // Pass the Purchase Invoice ID to callback
//             } else {
//                 frappe.msgprint('Failed to create purchase invoice');
//             }
//         }
//     });
// }

// function createPurchasePaymentEntry(frm, cdt, cdn, purchase_invoice) {
//     var row = locals[cdt][cdn];
//     var schedule_date = row.schedule_date;

//     // Fetch default cash account (paid_from)
//     frappe.call({
//         method: 'frappe.client.get_value',
//         args: {
//             doctype: 'Company',
//             fieldname: 'default_cash_account',
//             filters: {
//                 name: frm.doc.company
//             }
//         },
//         callback: function(r) {
//             if (r && r.message) {
//                 var default_cash_account = r.message.default_cash_account;

//                 // Create payment entry for purchase invoice
//                 frappe.call({
//                     method: 'property_management.property_management.doctype.tenancy.tenancy.create_purchase_payment_entry',
//                     args: {
//                         supplier: frm.doc.supplier,
//                         payment_amount: row.invoice_amount,
//                         paid_from: default_cash_account, // Paid from for Purchase Invoice
//                         purchase_invoice: purchase_invoice,
//                         posting_date: schedule_date,
//                         schedule_date: schedule_date,
//                         reference_no: row.reference_no,
//                         invoice_ref: purchase_invoice,
//                         doc: frm.doc.name
//                     },
//                     callback: function(response) {
//                         if (response.message) {
//                             frappe.model.set_value(cdt, cdn, 'payment_entry_purchase', response.message);
//                             frm.save('Update');
//                         } else {
//                             frappe.msgprint('Failed to create payment entry for purchase invoice');
//                         }
//                     }
//                 });
//             } else {
//                 frappe.msgprint('Failed to fetch default cash account');
//             }
//         }
//     });
// }
