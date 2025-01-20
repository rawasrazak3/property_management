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

# @frappe.whitelist()
# def bulk_asset_split(asset_name, split_details):
#     split_details = json.loads(split_details)

#     asset = frappe.get_doc("Asset", asset_name)
#     remaining_qty = asset.asset_quantity

#     for index, split in enumerate(split_details):
#         quantity_to_split = flt(split.get("quantity_to_split"))
#         row_name_prefix = split.get("name_prefix")

#         if quantity_to_split > remaining_qty:
#             frappe.throw(_("Row {0}: Quantity to split exceeds available quantity.").format(index + 1))

#         # Use the name_prefix from the row
#         new_asset_name = row_name_prefix

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

    # Fetch the current asset
    asset = frappe.get_doc("Asset", asset_name)
    remaining_qty = asset.asset_quantity  # Replace with your field for quantity

    for index, split in enumerate(split_details):
        quantity_to_split = flt(split.get("quantity_to_split"))
        row_name_prefix = split.get("name_prefix")

        if quantity_to_split > remaining_qty:
            frappe.throw(_("Row {0}: Quantity to split exceeds available quantity.").format(index + 1))

        # Use the name_prefix from the row to name the new asset
        new_asset_name = row_name_prefix

        # Perform the split
        new_asset = erpnext_split_asset(asset.name, quantity_to_split)
        new_asset.db_set("asset_name", new_asset_name)  # Set the custom name

        # Copy parent asset hierarchy and add current asset as parent
        parent_hierarchy = [{"parent_asset": asset.name}]
        if asset.get("parent_hierarchy"):
            parent_hierarchy += asset.get("parent_hierarchy")

        # Add parent hierarchy to child table
        for parent in parent_hierarchy:
            new_asset.append("custom_parent_heirarchy", {"parent_asset": parent["parent_asset"]})

        # Copy shareholder table from the parent asset to the child asset
        # if asset.get("custom_shareholder_table"):
        #     for shareholder in asset.get("custom_shareholder_table"):
        #         new_asset.append("custom_shareholder_table", {
        #             "shareholder": shareholder.shareholder,
        #             "shareholder_account": shareholder.shareholder_account,
        #             "contribution": shareholder.contribution,
        #             "amount": shareholder.amount,
        #             "no_expense_included": shareholder.no_expense_included,
        #             "actual_contribution": shareholder.actual_contribution,
        #             "actual_amount": shareholder.actual_amount,
        #             "is_shareholder_exit": shareholder.is_shareholder_exit
        #         })

        # Save the new asset with updated hierarchy
        new_asset.save(ignore_permissions=True)

        # Notify the user about the new asset creation
        frappe.msgprint(_("Created new asset {0} with quantity {1}.").format(new_asset_name, quantity_to_split))

        # Update the remaining quantity of the original asset
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
def create_shareholder_journal_entry_1(asset_name, company, mode_of_payment, shareholder, shareholder_account, amount,project=None):
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

    # Determine project if not provided
    if not project:
        # Fetch project from related data or provide a default value
        project = frappe.db.get_value("Asset", asset_name, "custom_project")
        if not project:
            frappe.throw("Project is required but could not be determined.")

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
                "reference_name": asset_name,
                "project": project
            },
            {
                "account": shareholder_account,
                "credit_in_account_currency": float(amount),
                "party_type": "Shareholder",
                "party": shareholder,
                "reference_type": "Asset",
                "reference_name": asset_name,
                "project": project
            }
        ],
        "user_remark": "Shareholder initial deposit"
    })
    journal_entry.insert()
    journal_entry.submit()

    return journal_entry.name
@frappe.whitelist()
def submit_asset_with_advance(self, method=None):
    # Check if there's an advance amount added
    if self.custom_advance_amount and self.custom_advance_amount > 0:
        # Ensure that mode of payment and tenant are filled
        if not self.custom_mode_of_payment or not self.custom_tenant:
            frappe.throw("Please enter the Mode of Payment and Tenant before submitting.")
        
        # Fetch the default account for the selected Mode of Payment
        mode_of_payment_account = frappe.db.get_value(
            "Mode of Payment Account",
            {"parent": self.custom_mode_of_payment,"company":self.company},
            "default_account"
        )
        
        if not mode_of_payment_account:
            frappe.throw(f"No default account found for Mode of Payment: {self.custom_mode_of_payment}")
        
        # Prepare the Journal Entry
        journal_entry = frappe.new_doc('Journal Entry')
        journal_entry.voucher_type = 'Journal Entry'
        journal_entry.posting_date = frappe.utils.nowdate()
        journal_entry.company = self.company
        journal_entry.user_remark = f'Advance Payment for Asset: {self.name}'

        # Add Credit Entry (Mode of Payment Account)
        journal_entry.append('accounts', {
            'account': mode_of_payment_account,
            'debit_in_account_currency': self.custom_advance_amount,
            'debit': self.custom_advance_amount,
            'reference_type': 'Asset',
            'reference_name': self.name
        })
        company_abbr = frappe.db.get_value("Company", self.company, "abbr")
        # Add Debit Entry (Tenant/Customer Account or Default "Debtors" Account)
        tenant_account = frappe.get_value('Company', self.company, 'default_advance_received_account') or "Security Deposit - " + company_abbr

        journal_entry.append('accounts', {
            'account': tenant_account,
            'credit_in_account_currency': self.custom_advance_amount,
            'credit': self.custom_advance_amount,
            'party_type': 'Customer',
            'party': self.custom_tenant,
            'reference_type': 'Asset',
            'reference_name': self.name
        })

        # Save and insert the Journal Entry
        journal_entry.insert()
        journal_entry.submit()
        frappe.db.commit()

        # Update the journal_entry_id field in the Asset document
        self.db_set('custom_journal_entry_id', journal_entry.name)

@frappe.whitelist()
def create_maintenance_journal_entry(self, method=None):
    # Check if there's a custom amount added
    if self.custom_amount > 0 and not self.custom_ref_journal_entry_id:
        # Ensure that mode of payment and tenant are filled
        if not self.custom_amount or not self.custom_tenants:
            frappe.throw("Please enter the Amount and Tenant before submitting.")

        # Fetch property details
        main_property = self.custom_against_property or self.name
        company_abbr = frappe.db.get_value("Company", self.company, "abbr")
        maintenance_account_name = f"{main_property}-Maintenance-{company_abbr}"

        mode_of_payment_account = frappe.db.get_value(
            "Mode of Payment Account",
            {"parent": self.custom_mode_of_payments,"company":self.company},
            "default_account"
        )
        
        if not mode_of_payment_account:
            frappe.throw(f"No default account found for Mode of Payment: {self.custom_mode_of_payments}")

        # Check if a maintenance account already exists
        maintenance_account = frappe.db.get_value(
            "Account",
            {"account_name": f"{main_property}-Maintenance", "company": self.company}
        )

        # If no account exists, create a new one
        if not maintenance_account:
            maintenance_account = frappe.get_doc({
                "doctype": "Account",
                "account_name": f"{main_property}-Maintenance",
                "parent_account": "Property Expense - " + company_abbr,
                "company": self.company,
                "is_group": 0
            }).insert().name

        # Fetch the tenant's default receivable account or fallback to 'Debtors'
        tenant_account = frappe.get_value('Company', self.company, 'default_receivable_account') or "Debtors - " + company_abbr

        # Create Journal Entry
        journal_entry = frappe.get_doc({
            "doctype": "Journal Entry",
            "posting_date": nowdate(),
            "company": self.company,
            "accounts": [
                {
                    "account": mode_of_payment_account,
                    "debit_in_account_currency": self.custom_amount,
                    'reference_type': 'Asset',
                    'reference_name': self.name
                },
                {
                    "account": maintenance_account,
                    "credit_in_account_currency": self.custom_amount,
                    'reference_type': 'Asset',
                    'reference_name': self.name,
                    'party_type': 'Customer',
                    'party': self.custom_tenants,
                }
            ],
            "user_remark": _("Maintenance Charge for Property {0}").format(self.name)
        })
        journal_entry.insert()
        journal_entry.submit()
        frappe.db.commit()

        # Update the journal_entry_id field in the Asset document
        self.db_set('custom_ref_journal_entry_id', journal_entry.name)

