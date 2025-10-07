# Copyright (c) 2025, Ketan Patel and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document


class ProfitPay(Document):
	pass
# In your custom app's Python file
# @frappe.whitelist()
# def fetch_assets_with_property_hierarchy(property_id, limit_page_length=100):
#     if not property_id:
#         return []

#     # Query to fetch assets where the property matches in the property_hierarchy child table
#     query = """
#         SELECT 
#             a.name, a.gfa_sqft, a.gross_purchase_amount , a.custom_profit,a.asset_name
#         FROM 
#             `tabAsset` a
#         LEFT JOIN 
#             `tabParent Asset` ph ON ph.parent = a.name
#         WHERE 
#             a.status = 'Sold'
#             AND ph.parent_asset = %(property_id)s
#         LIMIT %(limit)s
#     """
#     return frappe.db.sql(
#         query, 
#         {"property_id": property_id, "limit": int(limit_page_length)}, 
#         as_dict=True
#     )

@frappe.whitelist()
def fetch_assets_with_property_hierarchy(property_id, limit_page_length=100):
    if not property_id:
        return []

    query = """
        SELECT 
            a.name, a.gfa_sqft, a.gross_purchase_amount, a.custom_profit,
            a.asset_name, a.custom_sales_invoice_id
        FROM 
            `tabAsset` a
        LEFT JOIN 
            `tabParent Asset` ph ON ph.parent = a.name
        WHERE 
            a.status = 'Sold'
            AND ph.parent_asset = %(property_id)s
        LIMIT %(limit)s
    """

    assets = frappe.db.sql(
        query, 
        {"property_id": property_id, "limit": int(limit_page_length)}, 
        as_dict=True
    )

    for asset in assets:
        sales_invoice_id = asset.get("custom_sales_invoice_id")
        selling_amount = 0

        if sales_invoice_id:
            # get correct receivable account from Sales Invoice
            debit_account = frappe.db.get_value("Sales Invoice", sales_invoice_id, "debit_to")
            if debit_account:
                # use that dynamic account to fetch debit from GL Entry
                selling_amount = frappe.db.get_value(
                    "GL Entry",
                    {
                        "voucher_no": sales_invoice_id,
                        "account": debit_account,
                        "voucher_type": "Sales Invoice"
                    },
                    "debit"
                ) or 0

        asset["selling_amount"] = selling_amount

    return assets

# @frappe.whitelist()
# def fetch_assets(property_id, limit_page_length=100):
#     if not property_id:
#         return []

#     # Query to fetch assets where the property matches in the property_hierarchy child table
#     query = """
#         SELECT 
#             a.name, a.gfa_sqft, a.gross_purchase_amount , a.custom_profit,a.asset_name
#         FROM 
#             `tabAsset` a
#         WHERE 
#             a.name = %(property_id)s
#         LIMIT %(limit)s
#     """
#     return frappe.db.sql(
#         query, 
#         {"property_id": property_id, "limit": int(limit_page_length)}, 
#         as_dict=True
#     )
@frappe.whitelist()
def fetch_assets(property_id, limit_page_length=100):
    if not property_id:
        return []

    query = """
        SELECT 
            a.name, a.gfa_sqft, a.gross_purchase_amount, a.custom_profit,
            a.asset_name, a.custom_sales_invoice_id
        FROM 
            `tabAsset` a
        WHERE 
            a.name = %(property_id)s
        LIMIT %(limit)s
    """

    assets = frappe.db.sql(
        query, 
        {"property_id": property_id, "limit": int(limit_page_length)}, 
        as_dict=True
    )

    for asset in assets:
        sales_invoice_id = asset.get("custom_sales_invoice_id")
        selling_amount = 0

        if sales_invoice_id:
            # get correct receivable account from Sales Invoice
            debit_account = frappe.db.get_value("Sales Invoice", sales_invoice_id, "debit_to")
            if debit_account:
                # use that dynamic account to fetch debit from GL Entry
                selling_amount = frappe.db.get_value(
                    "GL Entry",
                    {
                        "voucher_no": sales_invoice_id,
                        "account": debit_account,
                        "voucher_type": "Sales Invoice"
                    },
                    "debit"
                ) or 0
        asset["selling_amount"] = selling_amount

    return assets

    # for asset in assets:
    #     sales_invoice_id = asset.get("custom_sales_invoice_id")
    #     print("------sales invoice ------",sales_invoice_id)
    #     selling_amount = 0

    #     if sales_invoice_id:
    #         gl_entry = frappe.db.get_value(
    #             "GL Entry",
    #             {
    #                 "voucher_no": sales_invoice_id,
    #                 "account": "Debtors-MH",
    #                 "voucher_type": "Sales Invoice"
    #             },
    #             "debit"
    #         )
    #         print("-------------------------sell amnt",gl_entry)
    #         if gl_entry:
    #             print("-------------------------sell amnt",gl_entry)
    #             selling_amount = gl_entry

    #     asset["selling_amount"] = selling_amount

    # return assets

@frappe.whitelist()
def after_save_profit_pay(doc, method):
    # Ensure all calculations are dynamic and save changes properly
    selected_shareholder = doc.shareholder
    main_property = doc.property
    total_profit = 0  # Initialize total profit
    total_profits = 0
    total_contribution = 0
    contribution = doc.contribution

    # Iterate through each row in the child table
    for asset in doc.sold_property_table:
        property_name = asset.property_name
        profit = asset.profit
        # Accumulate the total profit
        if profit:
            total_profits += profit

        # Fetch shareholder contribution for the specific property
        shareholder_contribution = frappe.db.get_value(
            "Shareholder Property",
            {"parent": property_name, "shareholder": selected_shareholder},
            "contribution"
        )

        # Calculate shareholder profit for the current property
        shareholder_profit = 0
        if shareholder_contribution:
            shareholder_profit = (profit * shareholder_contribution) / 100
            total_profit += shareholder_profit

        # Update the child row's shareholder_profit field
        asset.shareholder_profit = shareholder_profit

    # Update the total profit for the selected shareholder
    doc.total_shareholder_profit = total_profit
    doc.total_profit = total_profits
    doc.total_contribution = total_profit + contribution
   
@frappe.whitelist()
def create_profit_payout_journal(profit_pay_id, mode_of_payment):
    mode_of_payment_account = frappe.db.get_value(
    "Mode of Payment Account",
    {"parent": mode_of_payment},
    "default_account"
    )

    if not mode_of_payment_account:
        frappe.throw(f"No default account found for Mode of Payment: {mode_of_payment}")

    # Fetch the Profit Pay document
    profit_pay_doc = frappe.get_doc('Profit Pay', profit_pay_id)
    asset = frappe.get_doc('Asset', profit_pay_doc.property)

    # Calculate total shareholder profit (positive = profit, negative = loss)
    total_shareholder_profit = round(profit_pay_doc.total_shareholder_profit, 3)

    # Prevent zero transactions
    if total_shareholder_profit == 0:
        frappe.throw("Total shareholder profit cannot be zero.")

    # Prepare the Journal Entry
    journal_entry = frappe.new_doc('Journal Entry')
    journal_entry.voucher_type = 'Journal Entry'
    journal_entry.posting_date = frappe.utils.nowdate()
    journal_entry.company = asset.company
    journal_entry.user_remark = f'Profit Payout for Asset: {asset.name}'

    # Track total debit and credit
    total_debit = 0
    total_credit = 0

    # Add Mode of Payment Entry (Depends on Profit/Loss)
    if total_shareholder_profit > 0:
        # Profit scenario: Credit mode_of_payment_account
        journal_entry.append('accounts', {
            'account': mode_of_payment_account,
            'credit_in_account_currency': total_shareholder_profit,
            'credit': total_shareholder_profit
        })
        total_credit += total_shareholder_profit
    else:
        # Loss scenario: Debit mode_of_payment_account
        journal_entry.append('accounts', {
            'account': mode_of_payment_account,
            'debit_in_account_currency': abs(total_shareholder_profit),
            'debit': abs(total_shareholder_profit)
        })
        total_debit += abs(total_shareholder_profit)

    # Add Shareholder Entries (Debit for profit distribution, Credit for loss recovery)
    for sold_property in profit_pay_doc.sold_property_table:
        contribution_amount = round(sold_property.shareholder_profit, 3)
        ref_name = sold_property.property_name

        if contribution_amount > 0:
            # Profit scenario (Debit to shareholders)
            journal_entry.append('accounts', {
                'account': profit_pay_doc.shareholder_account,
                'debit_in_account_currency': contribution_amount,
                'debit': contribution_amount,
                'party_type': 'Shareholder',
                'party': profit_pay_doc.shareholder,
                'project': asset.custom_project,
                'reference_type': 'Asset',
                'reference_name': ref_name
            })
            total_debit += contribution_amount

        elif contribution_amount < 0:
            # Loss scenario (Credit from shareholders)
            abs_amount = abs(contribution_amount)
            journal_entry.append('accounts', {
                'account': profit_pay_doc.shareholder_account,
                'credit_in_account_currency': abs_amount,
                'credit': abs_amount,
                'party_type': 'Shareholder',
                'party': profit_pay_doc.shareholder,
                'project': asset.custom_project,
                'reference_type': 'Asset',
                'reference_name': ref_name
            })
            total_credit += abs_amount

    # Ensure Total Debit = Total Credit (Balance Entry if Needed)
    difference = round(total_debit - total_credit, 3)

    if difference > 0:
        # Adjust credit to match debit
        journal_entry.append('accounts', {
            'account': mode_of_payment_account,
            'credit_in_account_currency': difference,
            'credit': difference
        })
    elif difference < 0:
        # Adjust debit to match credit
        journal_entry.append('accounts', {
            'account': profit_pay_doc.shareholder_account,
            'debit_in_account_currency': abs(difference),
            'debit': abs(difference),
            'party_type': 'Shareholder',
            'party': profit_pay_doc.shareholder
        })

    # Save and submit the Journal Entry
    journal_entry.insert()
    # journal_entry.submit()

    # Commit changes to ensure data consistency
    frappe.db.commit()

    return journal_entry.name

@frappe.whitelist()
def fetch_filtered_asset(property_id, shareholder_name, properties_list, limit_page_length=100):
    if not property_id:
        frappe.throw("Property ID is required.")
    if not shareholder_name:
        frappe.throw("Shareholder Name is required.")
    if not properties_list:
        frappe.log_error(f"Properties List received: {properties_list}", "Properties List Error")
        frappe.throw("Properties List is required and must be a non-empty list.")
    properties_list= json.loads(properties_list)
    # Safeguard against unreasonable limit values
    limit_page_length = min(int(limit_page_length), 1000)  # Restrict maximum limit

    try:
        # Fetch existing Profit Pay entries for the same property and shareholder
        profit_pay_query = """
            SELECT 
                sp.property_name AS existing_property_id
            FROM 
                `tabProfit Pay` pp
            LEFT JOIN 
                `tabSold Property Details` sp ON sp.parent = pp.name
            WHERE 
                pp.property = %(property_id)s
                AND pp.shareholder = %(shareholder_name)s
        """
        existing_entries = frappe.db.sql(
            profit_pay_query, 
            {"property_id": property_id, "shareholder_name": shareholder_name}, 
            as_dict=True
        )
        # Extract existing property IDs
        existing_property_ids = [
            entry['existing_property_id'] for entry in existing_entries if entry.get('existing_property_id')
        ]
        # Filter out properties already included in other Profit Pay entries
        unique_properties = []
        removed_properties = []  # To store removed properties for logging/debugging

        for property in properties_list:
            # if isinstance(property, str):
            #           current_property_id = property
            # else:
            current_property_id = property.get("property_name")
            if current_property_id in existing_property_ids:
                removed_properties.append(property)  # Capture removed properties
            else:
                unique_properties.append(property)

        # Log the removed entries
        if removed_properties:
            frappe.logger().info(f"Removed {len(removed_properties)} duplicate properties: {removed_properties}")

        # Return the filtered list of unique properties
        return unique_properties

    except Exception as e:
        frappe.log_error(message=str(e), title="Fetch Filtered Asset Error")
        return []








