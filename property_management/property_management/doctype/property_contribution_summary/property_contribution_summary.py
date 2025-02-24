# Copyright (c) 2025, Ketan Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PropertyContributionSummary(Document):
	pass

@frappe.whitelist()
def get_property_contribution_details(property_name):
    # Fetch total expense from 'Expense Property' DocType
    total_expense = frappe.db.sql("""
        SELECT SUM(total_expense_amount) FROM `tabExpense Property`
        WHERE property=%s
    """, (property_name,))[0][0] or 0

    # Fetch actual contribution from 'Property Shareholder' DocType
    actual_contribution = frappe.db.get_value('Property Shareholder', {'property': property_name}, 'actual_property_amount') or 0

    # Fetch all columns from the 'shareholder_table' inside the 'Asset' DocType
    shareholder_contributions = []
    asset = frappe.get_value('Asset', {'name': property_name}, 'name')

    if asset:
        shareholder_entries = frappe.get_all(
            'Shareholder Property',  # Child table name inside 'Asset'
            filters={'parent': asset},  # Parent is the Asset DocType
            fields=['*']  # Fetch all fields
        )
        shareholder_contributions = shareholder_entries if shareholder_entries else []

    # Calculate total contribution
    total_contribution = actual_contribution + total_expense

    return {
        "total_expense": total_expense,
        "actual_contribution": actual_contribution,
        "total_contribution": total_contribution,
        "shareholder_contribution": shareholder_contributions  # Now contains full table data
    }
