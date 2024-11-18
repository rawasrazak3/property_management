# Copyright (c) 2024, Ketan Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, nowdate


class ExpenseProperty(Document):
	pass

# In a custom Python file or server script
@frappe.whitelist()
def get_mode_of_payment_account(mode_of_payment):
    account = frappe.db.get_value("Mode of Payment Account", {"parent": mode_of_payment}, "default_account")
    return account


# @frappe.whitelist()
# def create_journal_entry_with_mode_of_payment(expense_property, mode_of_payment):
#     # Fetch the account for the selected mode of payment
#     mode_of_payment_account = frappe.db.get_value("Mode of Payment Account", {"parent": mode_of_payment}, "default_account")
#     if not mode_of_payment_account:
#         frappe.throw("No account found for the selected mode of payment.")

#     # Fetch the Expense Property document
#     expense_property_doc = frappe.get_doc("Expense Property", expense_property)
#     total_expense_amount = flt(expense_property_doc.total_expense_amount)
#     journal_entries = {}

#     # Iterate over each asset in the land_property child table
#     for asset_row in expense_property_doc.land_property:
#         asset_doc = frappe.get_doc("Asset", asset_row.property)
#         allocated_expense = flt(asset_row.allocated_expense_amount)

#         # Fetch shareholders for each asset from Shareholder Property table
#         for shareholder_row in asset_doc.custom_shareholder_table:
#             shareholder = shareholder_row.shareholder
#             contribution_percent = flt(shareholder_row.contribution)
#             shareholder_account = shareholder_row.shareholder_account

#             if not shareholder_account:
#                 frappe.throw(f"Shareholder {shareholder} does not have an account set in Asset {asset_row.property}.")

#             # Calculate allocation based on contribution percentage
#             allocation_amount = (allocated_expense * (contribution_percent / 100))

#             # Aggregate entries by shareholder and account
#             if shareholder not in journal_entries:
#                 journal_entries[shareholder] = {
#                     "account": shareholder_account,
#                     "party_type": "Shareholder",
#                     "party": shareholder,
#                     "credit_in_account_currency": 0
#                 }
#             journal_entries[shareholder]["credit_in_account_currency"] += allocation_amount

#     # Prepare the journal entry data
#     je_doc = frappe.get_doc({
#         "doctype": "Journal Entry",
#         "posting_date": nowdate(),
#         "accounts": [
#             # Debit entry using the mode of payment account
#             {
#                 "account": mode_of_payment_account,
#                 "debit_in_account_currency": total_expense_amount
#             },
#             # Credit entries for each unique shareholder and account
#             *[
#                 {
#                     "account": entry["account"],
#                     "party_type": entry["party_type"],
#                     "party": entry["party"],
#                     "credit_in_account_currency": entry["credit_in_account_currency"]
#                 }
#                 for entry in journal_entries.values()
#             ]
#         ]
#     })

#     # Save (but do not submit) the journal entry
#     je_doc.insert()

#     return je_doc.name  # Return the name of the created journal entry

@frappe.whitelist()
def create_journal_entry_with_mode_of_payment(expense_property, mode_of_payment):
    # Fetch the account for the selected mode of payment
    mode_of_payment_account = frappe.db.get_value("Mode of Payment Account", {"parent": mode_of_payment}, "default_account")
    if not mode_of_payment_account:
        frappe.throw("No account found for the selected mode of payment. Please set an account for this mode of payment.")

    # Fetch the Expense Property document
    expense_property_doc = frappe.get_doc("Expense Property", expense_property)
    total_expense_amount = flt(expense_property_doc.total_expense_amount)
    journal_entries = {}

    # Iterate over each asset in the land_property child table
    for asset_row in expense_property_doc.land_property:
        asset_doc = frappe.get_doc("Asset", asset_row.property)
        allocated_expense = flt(asset_row.allocated_expense_amount)

        # Fetch shareholders for each asset from Shareholder Property table
        for shareholder_row in asset_doc.custom_shareholder_table:
            # Skip shareholders with 'no_expense_included' checked
            if shareholder_row.no_expense_included:
                continue

            shareholder = shareholder_row.shareholder
            contribution_percent = flt(shareholder_row.contribution)
            shareholder_account = shareholder_row.shareholder_account

            if not shareholder_account:
                frappe.throw(f"Shareholder {shareholder} does not have an account set in Property {asset_row.property}.")

            # Calculate allocation based on contribution percentage
            allocation_amount = allocated_expense * (contribution_percent / 100)

            # Aggregate entries by shareholder and account
            if shareholder not in journal_entries:
                journal_entries[shareholder] = {
                    "account": shareholder_account,
                    "party_type": "Shareholder",
                    "party": shareholder,
                    "credit_in_account_currency": 0,
                    "reference_type": "Asset",  # Set reference type as Property
                    "reference_name": asset_row.property  # Set the specific property (asset) name
                }
            journal_entries[shareholder]["credit_in_account_currency"] += allocation_amount

    # Prepare the journal entry data without saving it yet
    je_doc = frappe.get_doc({
        "doctype": "Journal Entry",
        "posting_date": frappe.utils.nowdate(),
        "custom_is_expense_property": 1,  # Mark as related to Expense Property
        "accounts": [
            # Debit entry using the mode of payment account
            {
                "account": mode_of_payment_account,
                "debit_in_account_currency": total_expense_amount
            },
            # Credit entries for each unique shareholder and account, including reference details
            *[
                {
                    "account": entry["account"],
                    "party_type": entry["party_type"],
                    "party": entry["party"],
                    "credit_in_account_currency": entry["credit_in_account_currency"],
                    "reference_type": entry["reference_type"],  # Set reference type as Property
                    "reference_name": entry["reference_name"]   # Set the specific property (asset) name
                }
                for entry in journal_entries.values()
            ]
        ]
    })

    # Return the document data without saving it
    return je_doc.as_dict()  # Return the document data as a dictionary




# Custom script for Expense Property DocType

###################################################################
# class ExpenseProperty(Document):
#     def before_submit(self):
#         for item in self.land_property:
#             # Get the asset linked to this property row
#             asset = frappe.get_doc("Asset", item.property)
#             if asset:
#                 # Calculate the new gross purchase amount
#                 new_gross_purchase_amount = item.gross_amount + item.allocated_expense_amount
#                 # Update the asset's gross_purchase_amount field
#                 asset.db_set('gross_purchase_amount', new_gross_purchase_amount)
#                 frappe.db.commit()

# # Custom script for Expense Property DocType

# class ExpenseProperty(Document):
#     def before_submit(self):
#         # Step 1: Create the Journal Entry
#         je = frappe.new_doc("Journal Entry")
#         je.posting_date = self.posting_date
#         je.company = self.company
#         je.cheque_no = self.name  # Use the Expense Property ID as cheque_no
#         je.user_remark = f"Journal Entry for Expense Property {self.name}"
#         je.voucher_type = "Journal Entry"
#         je.cheque_date = self.posting_date

#         # Step 2: Add entries from Expense Property Expense child table
#         for expense_item in self.expense_account:
#             je.append("accounts", {
#                 "account": expense_item.expense_account,
#                 "debit_in_account_currency": expense_item.amount,
#                 "credit_in_account_currency": 0,
#                 "user_remark": expense_item.description
#             })

#         # Step 3: Fetch Mode of Payment Account for the specified Company
#         mode_of_payment_account = frappe.db.get_value("Mode of Payment Account", 
#                                                       {"parent": self.mode_of_payment, "company": self.company},
#                                                       "default_account")
#         if not mode_of_payment_account:
#             frappe.throw(f"No account found in Mode of Payment for company {self.company}.")

#         # Step 4: Add the Mode of Payment account entry (as a credit entry)
#         total_debit = sum([item.amount for item in self.expense_account])
#         je.append("accounts", {
#             "account": mode_of_payment_account,
#             "debit_in_account_currency": 0,
#             "credit_in_account_currency": total_debit,
#             "user_remark": f"Payment via {self.mode_of_payment}"
#         })

#         # Step 5: Insert and submit the Journal Entry
#         je.insert()
#         je.submit()
##############################################################################

class ExpenseProperty(Document):
    def before_submit(self):
        # Part 1: Update Asset gross_purchase_amount and custom_total_expenses
        for item in self.land_property:
            # Get the asset linked to this property row
            asset = frappe.get_doc("Asset", item.property)
            if asset:
                # Calculate the new gross purchase amount
                new_gross_purchase_amount = item.gross_amount + item.allocated_expense_amount
                # Update the asset's gross_purchase_amount field
                asset.db_set('gross_purchase_amount', new_gross_purchase_amount)
                
                # Update the asset's custom_total_expenses field
                updated_total_expenses = (asset.custom_total_expenses or 0) + item.allocated_expense_amount
                asset.db_set('custom_total_expenses', updated_total_expenses)

        # Part 2: Create the Journal Entry
        je = frappe.new_doc("Journal Entry")
        je.posting_date = self.posting_date
        je.company = self.company
        je.cheque_no = self.name  # Use the Expense Property ID as cheque_no
        je.user_remark = f"Journal Entry for Expense Property {self.name}"
        je.voucher_type = "Journal Entry"
        je.cheque_date = self.posting_date

        # Step 2: Add entries from Expense Property Expense child table
        for expense_item in self.expense_account:
            je.append("accounts", {
                "account": expense_item.expense_account,
                "debit_in_account_currency": expense_item.amount,
                "credit_in_account_currency": 0,
                "user_remark": expense_item.description
            })

        # Step 3: Fetch Mode of Payment Account for the specified Company
        mode_of_payment_account = frappe.db.get_value("Mode of Payment Account", 
                                                      {"parent": self.mode_of_payment, "company": self.company},
                                                      "default_account")
        if not mode_of_payment_account:
            frappe.throw(f"No account found in Mode of Payment for company {self.company}.")

        # Step 4: Add the Mode of Payment account entry (as a credit entry)
        total_debit = sum([item.amount for item in self.expense_account])
        je.append("accounts", {
            "account": mode_of_payment_account,
            "debit_in_account_currency": 0,
            "credit_in_account_currency": total_debit,
            "user_remark": f"Payment via {self.mode_of_payment}"
        })

        # Step 5: Insert and submit the Journal Entry
        je.insert()
        je.submit()
