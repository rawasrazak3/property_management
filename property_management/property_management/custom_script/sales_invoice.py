import frappe

def create_purchase_invoice_and_payment_entry_from_sales_invoice(doc, method):
    if doc.custom_is_service_invoice:
        # Filter items belonging to "Government Services"
        service_items = [item for item in doc.items if item.item_group == "Government Services"]

        if not service_items:
            frappe.msgprint("No 'Government Services' items found in the Sales Invoice.")
            return

        # Create Purchase Invoice
        purchase_invoice = frappe.new_doc("Purchase Invoice")
        purchase_invoice.supplier = doc.custom_supplier
        purchase_invoice.company = doc.company
        purchase_invoice.posting_date = doc.posting_date

        total_paid_amount = 0  # To store the total amount for payment entry

        # Add filtered items to the Purchase Invoice
        for item in service_items:
            purchase_invoice.append("items", {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "description": item.description,
                "qty": item.qty,
                "rate": item.rate,
                "amount": item.amount,
                "uom": item.uom,
                "stock_uom": item.stock_uom,
                "conversion_factor": item.conversion_factor,
                "expense_account": item.expense_account or frappe.get_value("Company", doc.company, "default_expense_account"),
                "cost_center": item.cost_center or frappe.get_value("Company", doc.company, "cost_center")
            })
            total_paid_amount += item.amount

        # Set taxes and charges if any exist in the Sales Invoice
        if doc.taxes:
            for tax in doc.taxes:
                purchase_invoice.append("taxes", {
                    "charge_type": tax.charge_type,
                    "account_head": tax.account_head,
                    "description": tax.description,
                    "rate": tax.rate,
                    "tax_amount": tax.tax_amount
                })

        # Link to Sales Invoice
        purchase_invoice.references = [{
            "reference_doctype": "Sales Invoice",
            "reference_name": doc.name
        }]

        # Insert and submit Purchase Invoice
        purchase_invoice.insert(ignore_permissions=True)
        purchase_invoice.submit()

        frappe.msgprint(f"Purchase Invoice {purchase_invoice.name} created for Supplier {doc.custom_supplier}.")

        # Create Payment Entry against the created Purchase Invoice
        mode_of_payment_account = frappe.db.get_value("Mode of Payment Account", {"parent": doc.custom_mode_of_payment}, "default_account")

        payment_entry = frappe.new_doc("Payment Entry")
        payment_entry.payment_type = "Pay"
        payment_entry.party_type = "Supplier"
        payment_entry.party = doc.custom_supplier
        payment_entry.company = doc.company
        payment_entry.paid_amount = total_paid_amount
        payment_entry.received_amount = total_paid_amount
        payment_entry.mode_of_payment = doc.custom_mode_of_payment
        payment_entry.paid_from = mode_of_payment_account  # Payment from account based on Mode of Payment
        payment_entry.paid_to = frappe.get_value("Company", doc.company, "default_payable_account")  # Payable account
        payment_entry.reference_no = purchase_invoice.name  # Reference to Purchase Invoice
        payment_entry.reference_date = purchase_invoice.posting_date
        payment_entry.source_exchange_rate = 1

        # Link Payment Entry to Purchase Invoice
        payment_entry.append("references", {
            "reference_doctype": "Purchase Invoice",
            "reference_name": purchase_invoice.name,
            "total_amount": total_paid_amount,
            "outstanding_amount": total_paid_amount,
            "allocated_amount": total_paid_amount
        })

        # Insert and submit Payment Entry
        payment_entry.insert(ignore_permissions=True)
        payment_entry.submit()

        frappe.msgprint(f"Payment Entry {payment_entry.name} created and linked to Purchase Invoice {purchase_invoice.name}.")

# def create_payment_entry_from_sales_invoice(doc, method):
#     # Check if the custom_is_service_invoice checkbox is checked
#     if doc.custom_is_service_invoice:
#         # Filter out items with item_group "Government Services" and sum their rate
#         total_paid_amount = sum(item.rate for item in doc.items if item.item_group == "Government Services")

#         # Fetch the mode of payment account based on custom_mode_of_payment
#         mode_of_payment_account = frappe.db.get_value("Mode of Payment Account", {"parent": doc.custom_mode_of_payment}, "default_account")

#         # Create Payment Entry
#         payment_entry = frappe.new_doc("Payment Entry")
#         payment_entry.payment_type = "Pay"
#         payment_entry.party_type = "Supplier"
#         payment_entry.party = doc.custom_supplier
#         payment_entry.company = doc.company
#         payment_entry.paid_amount = total_paid_amount
#         payment_entry.received_amount = total_paid_amount
#         payment_entry.mode_of_payment = doc.custom_mode_of_payment
#         payment_entry.paid_from = mode_of_payment_account  # Payment from account based on Mode of Payment
#         # payment_entry.paid_from_account_currency = "OMR"
#         payment_entry.paid_to = frappe.get_value("Company", doc.company, "default_payable_account")  # Set the payable account for the supplier
#         payment_entry.reference_no = doc.name
#         payment_entry.reference_date = doc.posting_date
#         payment_entry.source_exchange_rate = 1
        
#         # Insert and submit the Payment Entry
#         payment_entry.insert(ignore_permissions=True)
#         payment_entry.submit()
        
#         frappe.msgprint(f"Payment Entry {payment_entry.name} created for Supplier {doc.custom_supplier}.")

# def create_purchase_invoice_from_sales_invoice(doc, method):
#     if doc.custom_is_service_invoice:
#         # Filter items belonging to "Government Services"
#         service_items = [item for item in doc.items if item.item_group == "Government Services"]

#         if not service_items:
#             frappe.msgprint("No 'Government Services' items found in the Sales Invoice.")
#             return

#         # Create Purchase Invoice
#         purchase_invoice = frappe.new_doc("Purchase Invoice")
#         purchase_invoice.supplier = doc.custom_supplier
#         purchase_invoice.company = doc.company
#         purchase_invoice.posting_date = doc.posting_date

#         # Add filtered items to the Purchase Invoice
#         for item in service_items:
#             purchase_invoice.append("items", {
#                 "item_code": item.item_code,
#                 "item_name": item.item_name,
#                 "description": item.description,
#                 "qty": item.qty,
#                 "rate": item.rate,
#                 "amount": item.amount,
#                 "uom": item.uom,
#                 "stock_uom": item.stock_uom,
#                 "conversion_factor": item.conversion_factor,
#                 "expense_account": item.expense_account or frappe.get_value("Company", doc.company, "default_expense_account"),
#                 "cost_center": item.cost_center or frappe.get_value("Company", doc.company, "cost_center")
#             })

#         # Set taxes and charges if any exist in the Sales Invoice
#         if doc.taxes:
#             for tax in doc.taxes:
#                 purchase_invoice.append("taxes", {
#                     "charge_type": tax.charge_type,
#                     "account_head": tax.account_head,
#                     "description": tax.description,
#                     "rate": tax.rate,
#                     "tax_amount": tax.tax_amount
#                 })

#         # Link to Sales Invoice
#         purchase_invoice.references = [{
#             "reference_doctype": "Sales Invoice",
#             "reference_name": doc.name
#         }]

#         # Insert and submit Purchase Invoice
#         purchase_invoice.insert(ignore_permissions=True)
#         purchase_invoice.submit()

#         frappe.msgprint(f"Purchase Invoice {purchase_invoice.name} created for Supplier {doc.custom_supplier}.")

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
        if item.asset:
            prop = item.asset
        if item.income_account:
            income_account = item.income_account
            break
    if not income_account:
        frappe.throw("Income Account not found in Sales Invoice Items.")
    
    # Fetch credit and debit amounts from GL Entry
    gl_entry = frappe.get_all(
        "GL Entry",
        filters={
            "voucher_no": doc.name,
            "account": income_account,
            "voucher_type": "Sales Invoice"
        },
        fields=["credit", "debit"]
    )

    if not gl_entry:
        frappe.throw("GL Entry with the required credit or debit amount not found.")

    credit_amount = gl_entry[0].get("credit", 0)
    debit_amount = gl_entry[0].get("debit", 0)

    # Fetch property name from item table
    property_name = next(
        (item.item_name for item in doc.items if item.item_name), None
    )

    if not property_name:
        frappe.throw("Property (item name) not found in Sales Invoice items.")

    asset = frappe.get_all(
        "Asset",
        filters={"item_code": property_name, "split_from": ("is", "not set")},
        fields=["name", "custom_project"]
    )

    if not asset:
        frappe.throw(f"No Asset found for the property: {property_name}")

    # Extract the Asset name and project name
    asset_name = asset[0].get("name")
    project_name = asset[0].get("custom_project")

    # Fetch shareholder details for the property
    shareholders = frappe.get_all(
        "Shareholder Property",
        filters={"parent": asset_name, "parenttype": "Asset"},
        fields=["shareholder", "shareholder_account", "contribution", "amount"]
    )

    if not shareholders:
        frappe.throw(f"No shareholders found for the property: {property_name}")

    # Prepare journal entry accounts
    journal_entry_entries = []

    if credit_amount > 0:
        # Handle profit (credit case)
        # Debit income account
        journal_entry_entries.append({
            "account": income_account,
            "debit": credit_amount,
            'debit_in_account_currency': credit_amount,
            "credit_in_account_currency": 0,
            "project": project_name
        })

        # Credit shareholder accounts
        for shareholder in shareholders:
            share_amount = (credit_amount * shareholder.contribution) / 100
            journal_entry_entries.append({
                "account": shareholder.shareholder_account,
                "debit_in_account_currency": 0,
                "credit": share_amount,
                'credit_in_account_currency': share_amount,
                "party_type": "Shareholder",
                "party": shareholder.shareholder,
                "project": project_name
            })
        frappe.db.set_value("Asset", prop, "custom_profit", credit_amount)

    elif debit_amount > 0:
        # Handle loss (debit case)
        # Credit income account
        journal_entry_entries.append({
            "account": income_account,
            "credit": debit_amount,
            'credit_in_account_currency': debit_amount,
            "debit_in_account_currency": 0,
            "project": project_name
        })

        # Debit shareholder accounts
        for shareholder in shareholders:
            share_amount = (debit_amount * shareholder.contribution) / 100
            journal_entry_entries.append({
                "account": shareholder.shareholder_account,
                "debit": share_amount,
                'debit_in_account_currency': share_amount,
                "credit_in_account_currency": 0,
                "party_type": "Shareholder",
                "party": shareholder.shareholder,
                "project": project_name
            })
        frappe.db.set_value("Asset", prop, "custom_profit", -debit_amount)  # Negative for loss

    else:
        frappe.throw("Neither profit nor loss detected in the GL Entry.")

    # Create Journal Entry
    journal_entry = frappe.get_doc({
        "doctype": "Journal Entry",
        "voucher_type": "Journal Entry",
        "posting_date": doc.posting_date,
        "accounts": journal_entry_entries,
        "user_remark": f"Split income/loss from Sales Invoice {doc.name}"
    })
    journal_entry.insert(ignore_permissions=True)
    journal_entry.submit()

    frappe.logger().debug(f"Journal Entry {journal_entry.name} created successfully.")
