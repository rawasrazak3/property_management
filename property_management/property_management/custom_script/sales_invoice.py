import frappe

def create_payment_entry_from_sales_invoice(doc, method):
    # Check if the custom_is_service_invoice checkbox is checked
    if doc.custom_is_service_invoice:
        # Filter out items with item_group "Government Services" and sum their rate
        total_paid_amount = sum(item.rate for item in doc.items if item.item_group == "Government Services")

        # Fetch the mode of payment account based on custom_mode_of_payment
        mode_of_payment_account = frappe.db.get_value("Mode of Payment Account", {"parent": doc.custom_mode_of_payment}, "default_account")

        # Create Payment Entry
        payment_entry = frappe.new_doc("Payment Entry")
        payment_entry.payment_type = "Pay"
        payment_entry.party_type = "Supplier"
        payment_entry.party = doc.custom_supplier
        payment_entry.company = doc.company
        payment_entry.paid_amount = total_paid_amount
        payment_entry.received_amount = total_paid_amount
        payment_entry.mode_of_payment = doc.custom_mode_of_payment
        payment_entry.paid_from = mode_of_payment_account  # Payment from account based on Mode of Payment
        # payment_entry.paid_from_account_currency = "OMR"
        payment_entry.paid_to = frappe.get_value("Company", doc.company, "default_payable_account")  # Set the payable account for the supplier
        payment_entry.reference_no = doc.name
        payment_entry.reference_date = doc.posting_date
        payment_entry.source_exchange_rate = 1
        
        # Insert and submit the Payment Entry
        payment_entry.insert(ignore_permissions=True)
        payment_entry.submit()
        
        frappe.msgprint(f"Payment Entry {payment_entry.name} created for Supplier {doc.custom_supplier}.")
