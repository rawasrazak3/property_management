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
    split_properties = frappe.get_all(
        'Asset',  # Adjust to your DocType name if different
        filters={'split_from': main_property},
        fields=['name']
    )

    # Shareholder data from the child table
    shareholder_entries = [
        {
            'shareholder': row.shareholder,
            'contribution': row.contribution,
            'amount': row.amount,
            'no_expense_included': row.no_expense_included,
            'is_shareholder_exit':row.is_shareholder_exit
        }
        for row in doc.shareholder
    ]

    # Update main property and split properties
    properties_to_update = [main_property] + [p['name'] for p in split_properties]
    for property_name in properties_to_update:
        append_shareholders_to_asset(property_name, shareholder_entries)

def append_shareholders_to_asset(asset_name, shareholder_entries):
    # Fetch the Asset document
    asset = frappe.get_doc('Asset', asset_name)

    # Append shareholder data to the child table
    for entry in shareholder_entries:
        asset.append('custom_shareholder_table', entry)

    # Save the updated document
    asset.save()
