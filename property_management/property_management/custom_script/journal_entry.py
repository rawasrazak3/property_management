import frappe
from frappe.utils import flt

# @frappe.whitelist()
# def update_shareholder_expenses(journal_entry, method=None):
#     try:
#         # Fetch the submitted Journal Entry
#         je_doc = frappe.get_doc("Journal Entry", journal_entry)

#         # Check if this Journal Entry is linked to an Expense Property
#         if not je_doc.custom_is_expense_property:
#             return  # Exit if not related to an Expense Property

#         # Iterate over accounts in the Journal Entry
#         for entry in je_doc.accounts:
#             # Check if entry has reference_type as 'Asset' and a reference_name
#             if entry.reference_type == "Asset" and entry.reference_name:
#                 # Get the Property document by its reference_name
#                 property_doc = frappe.get_doc("Asset", entry.reference_name)

#                 # Check for the specific shareholder in the custom_shareholder_table
#                 shareholder_found = False
#                 for row in property_doc.custom_shareholder_table:
#                     # Update only if the shareholder matches and there is a credit amount
#                     if row.shareholder == entry.party and entry.credit_in_account_currency > 0:
#                         # Calculate and add the expense amount to current and total expense
#                         allocated_expense = flt(entry.credit_in_account_currency)
#                         row.amount = flt(row.amount) + allocated_expense
#                         row.total_expense = flt(row.total_expense) + allocated_expense
#                         shareholder_found = True

#                 # Recalculate contributions for all rows
#                 total_amount = sum(flt(row.amount) for row in property_doc.custom_shareholder_table)

#                 if total_amount > 0:
#                     for row in property_doc.custom_shareholder_table:
#                         row.contribution = (flt(row.amount) / total_amount) * 100

#                 # Save the Property document if any shareholder was found and updated
#                 if shareholder_found:
#                     property_doc.save()

#     except Exception as e:
#         # Log the error without using the `level` argument
#         frappe.logger("update_shareholder_expenses").error(f"Error updating shareholder expenses: {str(e)}")

# # Trigger this function on Journal Entry submission
# def on_submit_journal_entry(doc, method):
#     if doc.voucher_type == "Journal Entry":
#         update_shareholder_expenses(doc.name, method)

@frappe.whitelist()
def update_shareholder_expenses(journal_entry, method=None):
    try:
        # Fetch the submitted Journal Entry
        je_doc = frappe.get_doc("Journal Entry", journal_entry)

        # Check if this Journal Entry is linked to an Expense Property
        if not je_doc.custom_is_expense_property:
            return  # Exit if not related to an Expense Property
        if je_doc.custom_expense_property:
            frappe.db.set_value("Expense Property", je_doc.custom_expense_property, "journal_entry", je_doc.name)
            frappe.db.commit()
            
        # Iterate over accounts in the Journal Entry
        for entry in je_doc.accounts:
            # Check if entry has reference_type as 'Asset' and a reference_name
            if entry.reference_type == "Asset" and entry.reference_name:
                # Update the main property and its sub-properties
                update_main_and_sub_properties(entry.reference_name, entry)

    except Exception as e:
        # Log the error
        frappe.logger("update_shareholder_expenses").error(f"Error updating shareholder expenses: {str(e)}")


def update_main_and_sub_properties(main_property_name, entry):
    """
    Update the main property and its sub-properties based on the hierarchy.
    """
    # Fetch the main property document
    main_property_doc = frappe.get_doc("Asset", main_property_name)

    # Update the main property if its status is not "Sold"
    if main_property_doc.status.lower() != "sold":
        update_property(main_property_doc, entry)

    # Fetch sub-properties linked to the main property
    sub_properties = fetch_sub_properties(main_property_name)

    for sub_property in sub_properties:
        if sub_property["status"].lower() != "sold":
            sub_property_doc = frappe.get_doc("Asset", sub_property["name"])
            update_property(sub_property_doc, entry)


def update_property(property_doc, entry):
    """
    Update the expenses and contributions for a single property.
    """
    # Update the expenses for shareholders in the property
    shareholder_found = False
    for row in property_doc.custom_shareholder_table:
        # Update only if the shareholder matches and there is a credit amount
        if row.shareholder == entry.party and entry.credit_in_account_currency > 0:
            # Calculate and add the expense amount to current and total expense
            allocated_expense = flt(entry.credit_in_account_currency)
            row.amount = flt(row.amount) + allocated_expense
            row.total_expense = flt(row.total_expense) + allocated_expense
            shareholder_found = True

    # Recalculate contributions for all rows
    total_amount = sum(flt(row.amount) for row in property_doc.custom_shareholder_table)

    if total_amount > 0:
        for row in property_doc.custom_shareholder_table:
            row.contribution = (flt(row.amount) / total_amount) * 100

    # Save the Property document if any shareholder was found and updated
    if shareholder_found:
        property_doc.save()

def fetch_sub_properties(main_property_name):
    """
    Fetch sub-properties where the 'parent_asset' field in the 'custom_parent_heirarchy' child table
    matches the main property name.
    """
    query = """
        SELECT parent AS name
        FROM `tabParent Asset`
        WHERE parent_asset = %s
    """
    sub_properties = frappe.db.sql(query, (main_property_name,), as_dict=True)

    # Fetch Asset details for the resulting sub-properties
    if sub_properties:
        sub_property_names = [row["name"] for row in sub_properties]
        assets = frappe.get_all(
            "Asset",
            filters={"name": ["in", sub_property_names]},
            fields=["name", "status"]
        )
        return assets
    return []
# Trigger this function on Journal Entry submission
def on_submit_journal_entry(doc, method):
    if doc.voucher_type == "Journal Entry":
        update_shareholder_expenses(doc.name, method)

@frappe.whitelist()
def update_shareholder_exit(journal_entry, method=None):
    try:
        # Start logging
        frappe.logger("update_shareholder_exit").info(f"Starting update_shareholder_exit for Journal Entry: {journal_entry}")

        # Fetch the submitted Journal Entry
        je_doc = frappe.get_doc("Journal Entry", journal_entry)
        frappe.logger("update_shareholder_exit").info(f"Journal Entry {je_doc.name} fetched successfully.")

        # Check if this Journal Entry is marked for Shareholder Exit
        if not je_doc.custom_is_shareholder_exit:
            frappe.logger("update_shareholder_exit").info(f"Journal Entry {je_doc.name} is not marked for Shareholder Exit. Exiting.")
            return

        # Define the target shareholder ID for transfer
        target_shareholder = "ACC-SH-2024-00001"
        frappe.logger("update_shareholder_exit").info(f"Target Shareholder ID for transfer: {target_shareholder}")

        # Iterate over accounts in the Journal Entry
        for entry in je_doc.accounts:
            # Logging account details
            frappe.logger("update_shareholder_exit").info(
                f"Processing account line with reference_type: {entry.reference_type}, "
                f"reference_name: {entry.reference_name}, party: {entry.party}, credit_amount: {entry.credit_in_account_currency}"
            )

            if entry.reference_type == "Asset" and entry.reference_name:
                # Fetch the Asset document
                asset_doc = frappe.get_doc("Asset", entry.reference_name)
                frappe.logger("update_shareholder_exit").info(f"Fetched Asset: {asset_doc.name}")

                # Check for the specific shareholder in the custom_shareholder_table
                shareholder_found = False
                shareholder_value_to_transfer = 0

                # Locate the specified shareholder
                for row in asset_doc.custom_shareholder_table:
                    frappe.logger("update_shareholder_exit").info(
                        f"Checking shareholder in Asset table - Shareholder: {row.shareholder}, "
                        f"Amount: {row.amount}, Contribution: {row.contribution}%"
                    )

                    if row.shareholder == entry.party:
                        shareholder_value_to_transfer = flt(row.amount)
                        frappe.logger("update_shareholder_exit").info(
                            f"Match found! Removing shareholder {entry.party} with value: {shareholder_value_to_transfer}"
                        )
                        # Remove the shareholder from the table
                        asset_doc.custom_shareholder_table.remove(row)
                        shareholder_found = True
                        break

                # If shareholder was found, proceed with the transfer
                if shareholder_found:
                    frappe.logger("update_shareholder_exit").info(f"Transferring {shareholder_value_to_transfer} to {target_shareholder}")

                    # Find or create the target shareholder row
                    target_row = None
                    for row in asset_doc.custom_shareholder_table:
                        if row.shareholder == target_shareholder:
                            target_row = row
                            break

                    if target_row:
                        frappe.logger("update_shareholder_exit").info(
                            f"Target shareholder {target_shareholder} found. Updating amount from {target_row.amount} to {target_row.amount + shareholder_value_to_transfer}"
                        )
                        target_row.amount += shareholder_value_to_transfer
                    else:
                        frappe.logger("update_shareholder_exit").info(
                            f"Target shareholder {target_shareholder} not found. Adding new entry with amount: {shareholder_value_to_transfer}"
                        )
                        # Append new row for the target shareholder
                        new_row = asset_doc.append('custom_shareholder_table', {})
                        new_row.shareholder = target_shareholder
                        new_row.amount = shareholder_value_to_transfer
                        new_row.total_expense = 0
                        new_row.contribution = 0

                    # Recalculate contributions
                    total_amount = sum(flt(row.amount) for row in asset_doc.custom_shareholder_table)
                    frappe.logger("update_shareholder_exit").info(f"Total amount for contribution recalculation: {total_amount}")

                    if total_amount > 0:
                        for row in asset_doc.custom_shareholder_table:
                            old_contribution = row.contribution
                            row.contribution = (flt(row.amount) / total_amount) * 100
                            frappe.logger("update_shareholder_exit").info(
                                f"Updated contribution for shareholder {row.shareholder}: from {old_contribution}% to {row.contribution}%"
                            )

                    # Save the Asset document
                    asset_doc.save()
                    frappe.db.commit()
                    frappe.logger("update_shareholder_exit").info(f"Asset {asset_doc.name} updated successfully and changes committed.")

                else:
                    frappe.logger("update_shareholder_exit").info(f"No matching shareholder found in Asset {asset_doc.name} for party {entry.party}")

    except Exception as e:
        # Log the error with detailed information
        frappe.logger("update_shareholder_exit").error(f"Error in update_shareholder_exit for Journal Entry {journal_entry}: {str(e)}")


# Trigger this function on Journal Entry submission
def on_submit_journal_entry(doc, method):
    if doc.voucher_type == "Journal Entry":
        update_shareholder_exit(doc.name, method)