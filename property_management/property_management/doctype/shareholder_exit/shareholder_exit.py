# Copyright (c) 2025, Ketan Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class ShareholderExit(Document):
	pass
@frappe.whitelist()
def create_shareholder_exit_journal_entry(asset, shareholder, mode_of_payment, contribution, exit_amount, company, date=None, project=None, shareholder_account=None):
    from datetime import datetime

    if not mode_of_payment:
        frappe.throw("Mode of Payment is required.")

    if not exit_amount or float(exit_amount) <= 0:
        frappe.throw("Exit Amount must be greater than zero.")

    if not shareholder_account:
        frappe.throw("Shareholder Account is required.")

    if not date:
        date = datetime.now().date()

    # Get Mode of Payment Account
    mode_of_payment_account = frappe.db.get_value(
        "Mode of Payment Account",
        {"parent": mode_of_payment, "company": company},
        "default_account"
    )

    if not mode_of_payment_account:
        frappe.throw("No matching account found for the Mode of Payment in the specified company.")

    if not project:
        project = frappe.db.get_value("Asset", asset, "custom_project")
        if not project:
            frappe.throw("Project is required but could not be determined.")

    # Create Journal Entry
    journal_entry = frappe.get_doc({
        "doctype": "Journal Entry",
        "voucher_type": "Journal Entry",
        "company": company,
        "posting_date": date,
        "accounts": [
            {
                "account": mode_of_payment_account,
                "credit_in_account_currency": float(exit_amount),
                "reference_type": "Asset",
                "reference_name": asset,
                "project": project
            },
            {
               "account": shareholder_account,
                "debit_in_account_currency": float(exit_amount),
                "party_type": "Shareholder",
                "party": shareholder,
                "reference_type": "Asset",
                "reference_name": asset,
                "project": project
            }
        ],
        "custom_is_shareholder_exit": 1,  # ✅ Tick the checkbox while creating
        "user_remark": f"Shareholder Exit for Asset: {asset}"
    })

    journal_entry.insert(ignore_permissions=True)
    journal_entry.submit()

    return journal_entry.name
# Transfer to main

@frappe.whitelist()
def create_transfer_journal_entry(asset, mode_of_payment2, exit_amount, company, date=None, project=None):
    from datetime import datetime

    if not exit_amount or float(exit_amount) <= 0:
        frappe.throw("Exit Amount must be greater than zero.")

    if not date:
        date = datetime.now().date()

    # Fetch fixed shareholder info
    shareholder_id = "ACC-SH-2025-00001"
    shareholder = frappe.get_doc("Shareholder", shareholder_id)

    if not shareholder.custom_shareholder_account:
        frappe.throw("custom_shareholder_account is missing in the Shareholder record.")

    if not shareholder.company:
        frappe.throw("Company is missing in the Shareholder record.")

    # Get Mode of Payment Account
    mode_of_payment_account = frappe.db.get_value(
        "Mode of Payment Account",
        {"parent": mode_of_payment2, "company": company},
        "default_account"
    )

    if not mode_of_payment_account:
        frappe.throw("No matching account found for the selected Mode of Payment in this company.")

    # Auto-fetch project if not provided
    if not project:
        project = frappe.db.get_value("Asset", asset, "custom_project")

    journal_entry = frappe.get_doc({
        "doctype": "Journal Entry",
        "voucher_type": "Journal Entry",
        "company": company,
        "posting_date": date,
        "accounts": [
            {
               "account": mode_of_payment_account,
                "credit_in_account_currency": float(exit_amount),
                "reference_type": "Asset",
                "reference_name": asset,
                "project": project
            },
            {
                "account": shareholder.custom_shareholder_account,
                "debit_in_account_currency": float(exit_amount),
                "party_type": "Shareholder",
                "party": shareholder_id,
                "reference_type": "Asset",
                "reference_name": asset,
                "project": project
            }
        ],
        "user_remark": f"Transfer To Main - Shareholder: {shareholder_id}, Asset: {asset}"
    })

    journal_entry.insert(ignore_permissions=True)
    journal_entry.submit()

    return journal_entry.name

# updation in property shareholder doc


@frappe.whitelist()
def update_property_shareholder_child_table(shareholder_exit_name):
    # Fetch the Shareholder Exit document using the name
    shareholder_exit_doc = frappe.get_doc("Shareholder Exit", shareholder_exit_name)

    # Get the property from Shareholder Exit document
    property = shareholder_exit_doc.property

    # Fetch the Property Shareholder document by filtering using the property
    property_shareholder_doc = frappe.get_all(
        "Property Shareholder", 
        filters={"property": property},
        fields=["name"]
    )

    if not property_shareholder_doc:
        frappe.throw(f"No Property Shareholder document found for property: {property}")
    
    property_shareholder_name = property_shareholder_doc[0].name

    # Fetch the Property Shareholder document to edit the child table
    ps_doc = frappe.get_doc("Property Shareholder", property_shareholder_name)

    # Get the total amount from the Shareholder Exit document
    total_amount = float(shareholder_exit_doc.amount)  # Amount field from Shareholder Exit

    # Find the specific shareholder in the child table and update the values
    for row in ps_doc.shareholder:
        if row.shareholder == shareholder_exit_doc.shareholder:
            # Update the amount by reducing the exit amount
            row.amount = (row.amount or 0) - float(shareholder_exit_doc.exit_amount)
            # Update the contribution as a percentage of the total amount
            if total_amount > 0:
                row.contribution = (row.amount / total_amount) * 100

    # Find and update the main shareholder (ACC-SH-2025-00001)
    main_shareholder_id = "ACC-SH-2025-00001"  # The main shareholder ID
    main_found = False
    for row in ps_doc.shareholder:
        if row.shareholder == main_shareholder_id:
            # Update the amount by adding the exit amount
            row.amount = (row.amount or 0) + float(shareholder_exit_doc.exit_amount)
            # Update the contribution as a percentage of the total amount
            if total_amount > 0:
                row.contribution = (row.amount / total_amount) * 100
            main_found = True
            break

    # If the main shareholder is not found, add a new entry for the main shareholder
    if not main_found:
        ps_doc.append("shareholder", {
            "shareholder": main_shareholder_id,
            "property": property,
            "amount": float(shareholder_exit_doc.exit_amount),
            "contribution": (float(shareholder_exit_doc.exit_amount) / total_amount) * 100
        })

    # Save the Property Shareholder document after making the changes
    ps_doc.save(ignore_permissions=True)

    return "Property Shareholder child table updated successfully"






