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

# def on_submit_sales_invoice(doc, method):
#     # Fetch income account from Sales Invoice items
#     income_account = None
#     for item in doc.items:
#         if item.income_account:
#             income_account = item.income_account
#             break

#     if not income_account:
#         frappe.throw("Income Account not found in Sales Invoice Items.")
    
#     # Fetch the credit amount from GL Entry
#     gl_entry = frappe.get_all(
#         "GL Entry",
#         filters={
#             "voucher_no": doc.name,
#             "account": income_account,
#             "voucher_type": "Sales Invoice"
#         },
#         fields=["credit"]
#     )

#     if not gl_entry or not gl_entry[0].get("credit"):
#         frappe.throw("GL Entry with the required credit amount not found.")

#     credit_amount = gl_entry[0].get("credit")

#     # Fetch property name from item table
#     property_name = next(
#         (item.item_name for item in doc.items if item.item_name), None
#     )

#     if not property_name:
#         frappe.throw("Property (item name) not found in Sales Invoice items.")

#     asset = frappe.get_all(
#     "Asset",
#     filters={"item_code": property_name, "split_from": ("is", "not set")},
#     fields=["name"]
#     )

#     if not asset:
#         frappe.throw(f"No Asset found for the property: {property_name}")

#     # Extract the Asset name
#     asset_name = asset[0].get("name")

#     # Fetch shareholder details for the property
#     shareholders = frappe.get_all(
#         "Shareholder Property",
#         filters={"parent": asset_name, "parenttype": "Asset"},
#         fields=["shareholder", "shareholder_account", "contribution"]
#     )

#     if not shareholders:
#         frappe.throw(f"No shareholders found for the property: {property_name}")

#     # Prepare journal entry accounts
#     journal_entry_entries = []

#     # Debit income account
#     journal_entry_entries.append({
#         "account": income_account,
#         "debit": credit_amount,
#         'debit_in_account_currency': credit_amount,
#         "credit": 0,
#     })

#     # Credit shareholder accounts
#     for shareholder in shareholders:
#         share_amount = (credit_amount * shareholder.contribution) / 100
#         journal_entry_entries.append({
#             "account": shareholder.account,
#             "debit": 0,
#             "credit": share_amount,
#             'credit_in_account_currency': share_amount,
#         })

#     # Create Journal Entry
#     journal_entry = frappe.get_doc({
#         "doctype": "Journal Entry",
#         "voucher_type": "Journal Entry",
#         "posting_date": doc.posting_date,
#         "accounts": journal_entry_entries,
#         "user_remark": f"Split income from Sales Invoice {doc.name}"
#     })
#     journal_entry.insert()
#     journal_entry.save()

def on_submit_sales_invoice(doc, method):
    frappe.logger().debug(f"Sales Invoice {doc.name} submitted. Enqueuing journal entry creation.")
    # Enqueue journal entry creation after Sales Invoice submission
    frappe.enqueue(
        create_journal_entry_from_sales_invoice,
        sales_invoice=doc.name,
        queue="short",
        timeout=5
    )

def create_journal_entry_from_sales_invoice(sales_invoice):
    frappe.logger().debug(f"Starting journal entry creation for Sales Invoice: {sales_invoice}")
    # Fetch the submitted Sales Invoice
    doc = frappe.get_doc("Sales Invoice", sales_invoice)

    # Fetch income account from Sales Invoice items
    income_account = None
    for item in doc.items:
        if item.income_account:
            income_account = item.income_account
            break

    if not income_account:
        frappe.throw("Income Account not found in Sales Invoice Items.")
    
    # Fetch the credit amount from GL Entry
    gl_entry = frappe.get_all(
        "GL Entry",
        filters={
            "voucher_no": doc.name,
            "account": income_account,
            "voucher_type": "Sales Invoice"
        },
        fields=["credit"]
    )

    if not gl_entry or not gl_entry[0].get("credit"):
        frappe.throw("GL Entry with the required credit amount not found.")

    credit_amount = gl_entry[0].get("credit")

    # Fetch property name from item table
    property_name = next(
        (item.item_name for item in doc.items if item.item_name), None
    )

    if not property_name:
        frappe.throw("Property (item name) not found in Sales Invoice items.")

    asset = frappe.get_all(
        "Asset",
        filters={"item_code": property_name, "split_from": ("is", "not set")},
        fields=["name"]
    )

    if not asset:
        frappe.throw(f"No Asset found for the property: {property_name}")

    # Extract the Asset name
    asset_name = asset[0].get("name")

    # Fetch shareholder details for the property
    shareholders = frappe.get_all(
        "Shareholder Property",
        filters={"parent": asset_name, "parenttype": "Asset"},
        fields=["shareholder", "shareholder_account", "contribution"]
    )

    if not shareholders:
        frappe.throw(f"No shareholders found for the property: {property_name}")

    # Prepare journal entry accounts
    journal_entry_entries = []

    # Debit income account
    journal_entry_entries.append({
        "account": income_account,
        "debit": credit_amount,
        'debit_in_account_currency': credit_amount,
        "credit_in_account_currency": 0,
    })

    # Credit shareholder accounts
    for shareholder in shareholders:
        share_amount = (credit_amount * shareholder.contribution) / 100
        journal_entry_entries.append({
            "account": shareholder.shareholder_account,  # Fix account key
            "debit_in_account_currency": 0,
            "credit": share_amount,
            'credit_in_account_currency': share_amount,
            "party_type": "Shareholder",  # Adjust based on the type of party
            "party": shareholder.shareholder,  # This should be the shareholder's name
        })

    # Create Journal Entry
    journal_entry = frappe.get_doc({
        "doctype": "Journal Entry",
        "voucher_type": "Journal Entry",
        "posting_date": doc.posting_date,
        "accounts": journal_entry_entries,
        "user_remark": f"Split income from Sales Invoice {doc.name}"
    })
    journal_entry.insert(ignore_permissions=True)
    journal_entry.save()