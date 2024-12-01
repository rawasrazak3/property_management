frappe.ui.form.on('Tenancy Termination', {
    // refresh: function(frm) {
    //     // Add a custom button to calculate outstanding rent and amounts
    //     if (frm.doc.__islocal && frm.doc.tenant) {
    //         frm.add_custom_button(__('Calculate Outstanding Rent'), function() {
    //             // Call the method to calculate outstanding rent
    //             frappe.call({
    //                 method: 'property_management.property_management.doctype.tenancy_termination.tenancy_termination.calculate_outstanding_rent',
    //                 args: {
    //                     tenancy_name: frm.doc.tenancy,
    //                     tenancy_end_date: frm.doc.tenancy_end_date
    //                 },
    //                 callback: function(r) {
    //                     if (r.message) {
    //                         console.log(r.message);
    //                         frm.set_value('outstanding_rent', r.message);

    //                         // Perform the amounts calculation
    //                         calculate_amounts(frm);
    //                         frappe.msgprint(__('Outstanding rent and net amounts have been calculated.'));
    //                     }
    //                 }
    //             });
    //         }, __("Actions"));
    //     }
    // },
    
    calculate_outstanding_rent: function (frm) {
        calculate_amounts(frm);
        // Check if the form is not saved locally and has a tenant
        if (frm.doc.tenant && !frm.doc.docstatus==1) {
            frappe.call({
                method: 'property_management.property_management.doctype.tenancy_termination.tenancy_termination.calculate_outstanding_rent',
                args: {
                    tenancy_name: frm.doc.tenancy,
                    tenancy_end_date: frm.doc.tenancy_end_date
                },
                callback: function (r) {
                    if (r.message) {
                        console.log(r.message);
                        frm.set_value('outstanding_rent', r.message);

                        // Perform the amounts calculation
                        calculate_amounts(frm);
                        frappe.msgprint(__('Outstanding rent and net amounts have been calculated.'));
                    }
                }
            });
        } else {
            frappe.msgprint(__('Not Allowed'));
        }
    },
    
    
    // Trigger calculation when the "amount" field is changed
    amount: function(frm) {
        calculate_amounts(frm);
    }
});

function calculate_amounts(frm) {
    const outstanding = frm.doc.outstanding_rent || 0;
    const advance = frm.doc.advance_amounts || 0;
    const charge = frm.doc.amount || 0;

    const net_amount = outstanding - advance + charge;

    if (net_amount > 0) {
        frm.set_value('amount_receivable', net_amount);
        frm.set_value('amount_payable', 0);
    } else {
        frm.set_value('amount_payable', Math.abs(net_amount));
        frm.set_value('amount_receivable', 0);
    }
}

frappe.ui.form.on('Tenancy Termination', {
    // Trigger when the Tax Template is selected
    tax_template: function(frm) {
        if (frm.doc.tax_template) {
            // Fetch the tax rate corresponding to the selected tax template
            frappe.call({
                method: 'property_management.property_management.doctype.tenancy_termination.tenancy_termination.fetch_tax_data',
                args: {
                    template_name: frm.doc.tax_template
                },
                callback: function(r) {
                    if (r.message) {
                        console.log('Tax Data:', r.message);
                        // let total_tax_rate = 0;
            
                        // r.message.forEach(row => {
                        //     total_tax_rate += row.tax_rate;
                        // });
            
                        frm.set_value('tax_rate', r.message);
                        console.log(frm.doc.tax_rate);

                        // frm.refresh_field('tax_rate');
                    }
                
                    
                    // if (frm.doc.amount_receivable>0){
                    //     // Calculate tax amount based on the amount without tax
                    //     const amount_without_tax = frm.doc.amount_receivable || 0; // Assuming 'amount' is the base amount field
                    //     const tax_amount = (frm.doc.tax_rate / 100) * amount_without_tax;

                    //     // Set the tax amount and amount without tax fields
                    //     frm.set_value('tax_amount', tax_amount);
                    //     frm.set_value('amount_exc_tax', amount_without_tax);

                    //     // Calculate and update receivable or payable amount
                    //     const total_amount = amount_without_tax + tax_amount;
                    //     frm.set_value('amount_receivable', total_amount); // Update receivable amount
                    //     frm.set_value('amount_payable', 0); // Ensure payable is set to 0
                    // }
                    // else {
                    //     const amount_without_tax = frm.doc.amount_payable || 0; // Assuming 'amount' is the base amount field
                    //     const tax_amount = (frm.doc.tax_rate / 100) * amount_without_tax;

                    //     // Set the tax amount and amount without tax fields
                    //     frm.set_value('tax_amount', tax_amount);
                    //     frm.set_value('amount_exc_tax', amount_without_tax);

                    //     // Calculate and update receivable or payable amount
                    //     const total_amount = amount_without_tax + tax_amount;
                    //     frm.set_value('amount_receivable',0 ); // Update receivable amount
                    //     frm.set_value('amount_payable', total_amount); 
                    // }
                    if (frm.doc.amount_receivable>0){
                        // Calculate tax amount based on the amount without tax
                        const amount_without_tax = frm.doc.amount_receivable || 0; // Assuming 'amount' is the base amount field
                        const tax_amount = (frm.doc.tax_rate / 100) * frm.doc.amount;

                        // Set the tax amount and amount without tax fields
                        frm.set_value('tax_amount', tax_amount);
                        // frm.set_value('amount_exc_tax', amount_without_tax);

                        // Calculate and update receivable or payable amount
                        const total_amount = amount_without_tax + tax_amount;
                        frm.set_value('amount_receivable', total_amount); // Update receivable amount
                        frm.set_value('amount_payable', 0); // Ensure payable is set to 0
                    }
                    else {
                        const amount_without_tax = frm.doc.amount_payable || 0; // Assuming 'amount' is the base amount field
                        const tax_amount = (frm.doc.tax_rate / 100) * frm.doc.amount;

                        // Set the tax amount and amount without tax fields
                        frm.set_value('tax_amount', tax_amount);
                        // frm.set_value('amount_exc_tax', amount_without_tax);

                        // Calculate and update receivable or payable amount
                        const total_amount = amount_without_tax - tax_amount;
                        if (total_amount>0){
                            frm.set_value('amount_receivable',0 ); // Update receivable amount
                            frm.set_value('amount_payable', total_amount);
                        }
                        else{
                            frm.set_value('amount_receivable',Math.abs(total_amount) ); // Update receivable amount
                            frm.set_value('amount_payable', 0);
                        } 
                    }
                }
            });
        } else {
            // Clear the tax fields if no tax template is selected
            frm.set_value('tax_amount', 0);
            frm.set_value('amount_without_tax', 0);
            frm.set_value('amount_receivable', 0);
            frm.set_value('amount_payable', 0);
        }
    }
});
frappe.ui.form.on('Tenancy Termination', {
    refresh: function(frm) {
        if (frappe.route_options) {
            console.log("Received Route Options:", frappe.route_options);

            // Explicitly set values for each field
            frm.set_value('schedule_end_date', frappe.route_options.schedule_end_date || '');
            frm.set_value('advance_amounts', frappe.route_options.advance_amounts || 0);

            // Clear route options after setting values to avoid issues on reload
            frappe.route_options = null;
        }
    }
});
