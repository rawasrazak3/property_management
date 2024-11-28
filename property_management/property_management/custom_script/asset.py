import frappe
from frappe import _
from frappe.utils import nowdate, flt
from erpnext.assets.doctype.asset.asset import split_asset as erpnext_split_asset
import json

# @frappe.whitelist()
# def bulk_asset_split(asset_name, name_prefix, split_details):
#     split_details = json.loads(split_details)

#     asset = frappe.get_doc("Asset", asset_name)
#     remaining_qty = asset.asset_quantity

#     for index, split in enumerate(split_details):
#         quantity_to_split = int(split.get("quantity_to_split"))
        
#         if quantity_to_split > remaining_qty:
#             frappe.throw(_("Row {0}: Quantity to split exceeds available quantity.").format(index + 1))

#         # Construct the new asset name based on the prefix and index
#         new_asset_name = f"{name_prefix} {index + 1}"

#         # Perform the split and assign the new asset name
#         new_asset = erpnext_split_asset(asset.name, quantity_to_split)
#         new_asset.db_set("asset_name", new_asset_name)  # Set the custom name
#         frappe.msgprint(_("Created new asset {0} with quantity {1}.").format(new_asset_name, quantity_to_split))

#         remaining_qty -= quantity_to_split
#         asset.db_set("asset_quantity", remaining_qty)

#     return {"status": "success", "message": "Bulk asset split completed successfully."}

@frappe.whitelist()
def bulk_asset_split(asset_name, split_details):
    split_details = json.loads(split_details)

    asset = frappe.get_doc("Asset", asset_name)
    remaining_qty = asset.asset_quantity

    for index, split in enumerate(split_details):
        quantity_to_split = flt(split.get("quantity_to_split"))
        row_name_prefix = split.get("name_prefix")

        if quantity_to_split > remaining_qty:
            frappe.throw(_("Row {0}: Quantity to split exceeds available quantity.").format(index + 1))

        # Use the name_prefix from the row
        new_asset_name = row_name_prefix

        # Perform the split and assign the new asset name
        new_asset = erpnext_split_asset(asset.name, quantity_to_split)
        new_asset.db_set("asset_name", new_asset_name)  # Set the custom name
        frappe.msgprint(_("Created new asset {0} with quantity {1}.").format(new_asset_name, quantity_to_split))

        remaining_qty -= quantity_to_split
        asset.db_set("asset_quantity", remaining_qty)

    return {"status": "success", "message": "Bulk asset split completed successfully."}



@frappe.whitelist()
def create_shareholder_exit_journal_entry(asset, shareholder, mode_of_payment):
    # Fetch the Mode of Payment Account
    mode_of_payment_account = frappe.db.get_value("Mode of Payment Account", {"parent": mode_of_payment}, "default_account")
    if not mode_of_payment_account:
        frappe.throw("No account found for the selected mode of payment.")

    # Fetch the Asset document
    asset_doc = frappe.get_doc("Asset", asset)
    
    # Find the selected shareholder in the Shareholder Property table
    selected_shareholder_row = next((row for row in asset_doc.custom_shareholder_table if row.shareholder == shareholder), None)
    if not selected_shareholder_row:
        frappe.throw("Selected shareholder not found in asset.")

    # Retrieve the amount for the selected shareholder
    amount = flt(selected_shareholder_row.amount)
    if amount <= 0:
        frappe.throw("The amount for the selected shareholder must be greater than zero.")

    # Prepare details for Journal Entry
    shareholder_account = selected_shareholder_row.shareholder_account
    if not shareholder_account:
        frappe.throw(f"Shareholder {shareholder} does not have an account set in Asset {asset}.")

    # Create Journal Entry document
    je_doc = frappe.get_doc({
        "doctype": "Journal Entry",
        "posting_date": nowdate(),
        "custom_is_shareholder_exit": 1,
        "accounts": [
            {
                "account": shareholder_account,
                "party_type": "Shareholder",
                "party": shareholder,
                "debit_in_account_currency": amount
            },
            {
                "account": mode_of_payment_account,
                "credit_in_account_currency": amount
            }
        ]
    })

    # Save (but do not submit) the Journal Entry
    je_doc.insert()

    return je_doc.name  # Return the name of the created journal entry

##########################

@frappe.whitelist()
def create_journal_entry(asset_id, mode_of_payment):
    # Fetch the default account for the selected Mode of Payment
    mode_of_payment_account = frappe.db.get_value(
        "Mode of Payment Account",
        {"parent": mode_of_payment},
        "default_account"
    )

    if not mode_of_payment_account:
        frappe.throw(f"No default account found for Mode of Payment: {mode_of_payment}")

    # Fetch the Asset document
    asset_doc = frappe.get_doc('Asset', asset_id)

    # Get the Sales Invoice ID where the asset was sold
    sales_invoice_item = frappe.db.get_value(
        'Sales Invoice Item',
        {'asset': asset_id},
        'parent'
    )
    
    if not sales_invoice_item:
        frappe.throw("No Sales Invoice found for the asset.")

    # Fetch Sales Invoice details
    sales_invoice = frappe.get_doc('Sales Invoice', sales_invoice_item)
    grand_total = sales_invoice.grand_total

    # Prepare the Journal Entry
    journal_entry = frappe.new_doc('Journal Entry')
    journal_entry.voucher_type = 'Journal Entry'
    journal_entry.posting_date = frappe.utils.nowdate()
    journal_entry.company = asset_doc.company
    journal_entry.user_remark = f'Profit Split for Asset: {asset_id}'
    
    # Add Credit Entry (Mode of Payment Account)
    journal_entry.append('accounts', {
        'account': mode_of_payment_account,
        'credit_in_account_currency': grand_total,
        'credit': grand_total
    })

    # Calculate debit entries based on shareholder contributions
    total_contribution = sum([d.contribution for d in asset_doc.custom_shareholder_table])

    for shareholder in asset_doc.custom_shareholder_table:
        # Calculate the amount based on the contribution percentage
        contribution_amount = (grand_total * shareholder.contribution) / 100
        journal_entry.append('accounts', {
            'account': shareholder.shareholder_account,
            'debit_in_account_currency': contribution_amount,
            'debit': contribution_amount,
            'party_type': 'Shareholder',
            'party': shareholder.shareholder
        })

    # Save and redirect to the Journal Entry
    journal_entry.insert()
    frappe.db.commit()
    
    return journal_entry.name

@frappe.whitelist()
def create_shareholder_journal_entry_1(asset_name, company, mode_of_payment, shareholder, shareholder_account, amount):
    # Validate mode_of_payment
    if not mode_of_payment:
        frappe.throw("Mode of Payment is required.")

    # Validate amount
    if not amount or float(amount) <= 0:
        frappe.throw("Amount must be greater than zero.")

    # Check if mode_of_payment account exists for the given company
    mode_of_payment_account = frappe.db.get_value(
        "Mode of Payment Account",
        {"parent": mode_of_payment, "company": company},
        "default_account"
    )

    if not mode_of_payment_account:
        frappe.throw("No matching account found for the Mode of Payment in the specified company.")

    # Create Journal Entry
    journal_entry = frappe.get_doc({
        "doctype": "Journal Entry",
        "voucher_type": "Journal Entry",
        "company": company,
        "posting_date": nowdate(),
        "accounts": [
            {
                "account": mode_of_payment_account,
                "debit_in_account_currency": float(amount),
                "reference_type": "Asset",
                "reference_name": asset_name
            },
            {
                "account": shareholder_account,
                "credit_in_account_currency": float(amount),
                "party_type": "Shareholder",
                "party": shareholder,
                "reference_type": "Asset",
                "reference_name": asset_name
            }
        ],
        "user_remark": "Shareholder initial deposit"
    })
    journal_entry.insert()
    journal_entry.submit()

    return journal_entry.name