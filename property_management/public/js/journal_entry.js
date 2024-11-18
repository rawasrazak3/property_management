// Path: your_app/public/js/journal_entry.js

frappe.ui.form.on("Journal Entry", {
    on_submit: function(frm) {
        if (frm.doc.voucher_type === "Journal Entry" && frm.doc.custom_is_expense_property) {
            console.log("Attempting to update shareholder expenses...");
            frappe.call({
                method: "property_management.property_management.custom_script.journal_entry.update_shareholder_expenses",  // Adjust with actual path
                args: {
                    journal_entry: frm.doc.name
                },
                callback: function(response) {
                    if (response.message) {
                        console.log("Shareholder expenses updated successfully:", response.message);
                    } else {
                        console.log("No response message returned.");
                    }
                },
                error: function(error) {
                    console.error("Error updating shareholder expenses:", error);
                }
            });
        } else {
            console.log("Not an Journal Entry or not related to expense property. Skipping update.");
        }
    }
});
