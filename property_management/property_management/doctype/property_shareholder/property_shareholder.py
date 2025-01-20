# Copyright (c) 2025, Ketan Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PropertyShareholder(Document):
	pass


def update_property_shareholders(doc, method):
    # Main property selected in the Property Shareholder DocType
    main_property = doc.property
    if not main_property:
        frappe.throw("Main Property is required.")

    # Get all properties where "split_from" matches the main property
    # split_properties = frappe.get_all(
    #     'Asset',  # Adjust to your DocType name if different
    #     filters={'split_from': main_property},
    #     fields=['name']
    # )
    split_properties = frappe.db.sql(
    """
    SELECT parent 
    FROM `tabParent Asset`  -- Replace with your child table name
    WHERE parent_asset = %s
    """,
    main_property,
    as_dict=True
)

    # # Shareholder data from the child table
    # shareholder_entries = [
    #     {
    #         'shareholder': row.shareholder,
    #         'contribution': row.contribution,
    #         'amount': row.amount,
    #         'no_expense_included': row.no_expense_included,
    #         'is_shareholder_exit':row.is_shareholder_exit,
    #         'journal_entry':row.journal_entry,
    #         'actual_contribution': row.actual_contribution,
    #         'actual_amount' : row.actual_amount
    #     }
    #     for row in doc.shareholder
    # ]

    # Shareholder data from the child table
    shareholder_entries = []
    for row in doc.shareholder:
        # Only set actual_contribution and actual_amount if they are empty
        if not row.actual_contribution:
            row.actual_contribution = str(row.contribution)
        if not row.actual_amount:
            row.actual_amount = str(row.amount)
        
        # Collect the updated row data for further processing
        shareholder_entries.append({
            'shareholder': row.shareholder,
            'contribution': row.contribution,
            'amount': row.amount,
            'no_expense_included': row.no_expense_included,
            'is_shareholder_exit': row.is_shareholder_exit,
            'journal_entry': row.journal_entry,
            'actual_contribution': row.actual_contribution,
            'actual_amount': row.actual_amount
        })

    # Update main property and split properties
    properties_to_update = [main_property] + [p['parent'] for p in split_properties]
    for property_name in properties_to_update:
        append_shareholders_to_asset(property_name, shareholder_entries)

# def append_shareholders_to_asset(asset_name, shareholder_entries):
#     # Fetch the Asset document
#     asset = frappe.get_doc('Asset', asset_name)
#     for entry in shareholder_entries:
#         # Check if the entry already exists in the child table
#         is_duplicate = any(
#             row.shareholder == entry['shareholder']
#             and row.contribution == entry['contribution']
#             and row.amount == entry['amount']
#             for row in asset.custom_shareholder_table
#         )

#         # Append only if the entry is not a duplicate
#         if not is_duplicate:
#             asset.append('custom_shareholder_table', entry)
#     # Save the updated document
#     asset.save()

def append_shareholders_to_asset(asset_name, shareholder_entries):
    # Fetch the Asset document
    asset = frappe.get_doc('Asset', asset_name)
    
    for entry in shareholder_entries:
        # Check if the entry already exists in the child table
        existing_row = next(
            (row for row in asset.custom_shareholder_table if row.shareholder == entry['shareholder']),
            None
        )

        if existing_row:
            # Update the contribution and amount for the existing entry
            existing_row.contribution = entry.get('contribution', existing_row.contribution)
            existing_row.amount = entry.get('amount', existing_row.amount)
        else:
            # Append the new entry if no duplicate is found
            asset.append('custom_shareholder_table', entry)
    
    # Save the updated document
    asset.save()
