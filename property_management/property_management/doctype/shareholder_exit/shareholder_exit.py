# Copyright (c) 2025, Ketan Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
from datetime import datetime
from frappe import _, throw

class ShareholderExit(Document):
    pass

@frappe.whitelist()
def create_shareholder_exit_journal_entry(asset, shareholder, mode_of_payment, contribution, exit_amount, company, exit_date, project=None, shareholder_account=None):
    if not mode_of_payment:
        frappe.throw("Mode of Payment is required.")

    if not exit_amount or float(exit_amount) <= 0:
        frappe.throw("Exit Amount must be greater than zero.")

    if not shareholder_account:
        frappe.throw("Shareholder Account is required.")

    if not exit_date:
        exit_date = datetime.now().date()
    
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
        "posting_date": exit_date,  # ✅ use exit_date
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
        "custom_is_shareholder_exit": 1,
        "user_remark": f"Shareholder Exit for Asset: {asset}"
    })

    journal_entry.insert(ignore_permissions=True)
    journal_entry.save()

    return journal_entry.name

# Transfer to main
@frappe.whitelist()
def create_transfer_journal_entry(asset, mode_of_payment2, exit_amount, company, date=None, project=None,):
    if not exit_amount or float(exit_amount) <= 0:
        frappe.throw("Exit Amount must be greater than zero.")

    if not date:
        frappe.throw("Transfer Date is required.")

    # Fixed Shareholder ID
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

    # ✅ Create Journal Entry
    journal_entry = frappe.get_doc({
        "doctype": "Journal Entry",
        "voucher_type": "Journal Entry",
        "company": company,
        "posting_date": date,  # ✅ uses transfer_date
        "accounts": [
            {
                "account": shareholder.custom_shareholder_account,
                "credit_in_account_currency": float(exit_amount),
                "party_type": "Shareholder",
                "party": shareholder_id,
                "reference_type": "Asset",
                "reference_name": asset,
                "project": project
            },
            {
                "account": mode_of_payment_account,
                "debit_in_account_currency": float(exit_amount),
                "reference_type": "Asset",
                "reference_name": asset,
                "project": project
            }
        ],
        "user_remark": f"Transfer To Main - Shareholder: {shareholder_id}, Asset: {asset}"
    })

    journal_entry.insert()
    frappe.db.commit()

    return journal_entry.name

# Update in property shareholder doc
@frappe.whitelist()
def update_property_shareholder_child_table(shareholder_exit_name):
    # Fetch the Shareholder Exit document
    shareholder_exit_doc = frappe.get_doc("Shareholder Exit", shareholder_exit_name)

    exiting_shareholder = shareholder_exit_doc.shareholder
    property = shareholder_exit_doc.property
    exit_amount = float(shareholder_exit_doc.exit_amount)
    main_shareholder_id = "ACC-SH-2025-00001"
    
    # Fetch Property Shareholder document
    ps_doc_list = frappe.get_all(
        "Property Shareholder",
        filters={"property": property},
        fields=["name"]
    )

    if not ps_doc_list:
        frappe.throw(f"No Property Shareholder document found for property: {property}")
    
    ps_doc = frappe.get_doc("Property Shareholder", ps_doc_list[0].name)

    exiting_row = None
    main_row = None

    # Identify exiting and main shareholder rows
    for row in ps_doc.shareholder:
        if row.shareholder == exiting_shareholder:
            exiting_row = row
        if row.shareholder == main_shareholder_id:
            main_row = row

    if not exiting_row:
        frappe.throw(f"Shareholder {exiting_shareholder} not found in Property Shareholder.")
    
    if main_row:
        main_row.amount = (main_row.amount or 0) + exit_amount

    if shareholder_exit_doc.partial_payments:
        # last_payment = shareholder_exit_doc.partial_payments[-1]
        exiting_row.amount = (exiting_row.amount or 0) - exit_amount


    
    else:
        # Add main shareholder row if not present
        main_row = ps_doc.append("shareholder", {
            "shareholder": main_shareholder_id,
            "property": property,
            "amount": exit_amount
        })

    # Recalculate total and contribution
    new_total = sum((row.amount or 0) for row in ps_doc.shareholder)

    for row in ps_doc.shareholder:
        row.contribution = round(((row.amount or 0) / new_total) * 100, 2) if new_total else 0

    # Recalculate total_expense based on updated contribution
    # total_expenses = float(ps_doc.total_expenses or 0)
    # for row in ps_doc.shareholder:
    #     row.total_expense = (total_expenses * row.contribution) / 100.0

    # Remove rows with 0% contribution
    ps_doc.shareholder = [row for row in ps_doc.shareholder if float(row.contribution or 0) != 0]

    # Save the updated Property Shareholder document
    ps_doc.save(ignore_permissions=True)
    frappe.db.commit()

    return "Property Shareholder child table updated successfully"
# Checking the existing 
@frappe.whitelist()
def get_existing_shareholder_exit(property, shareholder):
    existing_exit = frappe.get_all("Shareholder Exit", 
        filters={
            "shareholder": shareholder,
            "property": property,
            "docstatus": ["in", [0, 1]]  # Check if the document is Draft (0) or Submitted (1)
        },
        fields=["name"])
    if existing_exit:
        return existing_exit[0].name  # Return the document name if found (for redirect)
    return None





class ShareholderExit(Document):
    def validate(self):
        # Allow saving in Draft without validation
        if self.docstatus == 0:
            return

        # For Submit: Ensure row counts match before allowing submission
        if self.docstatus == 1:
            count_partial = len(self.partial_payments)
            count_transfer = len(self.transfer_table)

            if count_partial != count_transfer:
                frappe.throw(_("The number of rows in Partial Payments and Transfer Table must be equal to submit."))

    def before_submit(self):
        # Double-check at submit level too
        count_partial = len(self.partial_payments)
        count_transfer = len(self.transfer_table)

        if count_partial != count_transfer:
            frappe.throw(_("You cannot submit. Row counts in Partial Payments and Transfer Table must match."))

    def on_update_after_submit(self):
        # For Update after Submit: Don't prevent save, but block submission if row counts mismatch
        count_partial = len(self.partial_payments)
        count_transfer = len(self.transfer_table)

        if count_partial != count_transfer:
            frappe.msgprint("Row count mismatch in Partial Payments and Transfer Table. Please correct and resubmit.")
