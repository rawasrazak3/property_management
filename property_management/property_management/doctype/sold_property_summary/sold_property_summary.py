# Copyright (c) 2025, Ketan Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SoldPropertySummary(Document):
	pass
# In your custom app's Python file
@frappe.whitelist()
def fetch_assets_with_property_hierarchy(property_id, limit_page_length=100):
    if not property_id:
        return []

    # Query to fetch assets where the property matches in the property_hierarchy child table
    query = """
        SELECT 
            a.name, a.gfa_sqft, a.gross_purchase_amount , a.custom_profit,a.asset_name
        FROM 
            `tabAsset` a
        LEFT JOIN 
            `tabParent Asset` ph ON ph.parent = a.name
        WHERE 
            a.status = 'Sold'
            AND ph.parent_asset = %(property_id)s
        LIMIT %(limit)s
    """
    return frappe.db.sql(
        query, 
        {"property_id": property_id, "limit": int(limit_page_length)}, 
        as_dict=True
    )
# @frappe.whitelist()
# def after_save_sold_property_summary(doc, method):
#     # Ensure the 'main_property' field is available in the Sold Property Summary DocType
#     main_property = doc.property
    
#     for asset in doc.sold_property_table:
#         profit = asset.profit
        
#         # Fetch shareholder shares based on the main_property
#         shareholders = frappe.get_all(
#             "Shareholder Property",
#             filters={"parent": main_property},
#             fields=["shareholder", "contribution"]
#         )
        
#         # Calculate each shareholder's share of the profit
#         shareholder_shares = []
#         for shareholder in shareholders:
#             share_amount = (profit * shareholder.contribution) / 100
#             shareholder_shares.append(
#                 f"{shareholder.shareholder}: {share_amount:.2f}"
#             )
        
#         # Create a record in the Sold Property Summary child table
#         doc.append("sold_property_table", {

#             "shareholder_shares": "\n".join(shareholder_shares),
#         })
    
#     # Save the Sold Property Summary document after appending details
#     doc.save()



# @frappe.whitelist()
# def after_save_sold_property_summary(doc, method):
#     # Iterate through each property in the sold_property_table
#     for asset in doc.sold_property_table:
#         property_name = asset.property_name  # Assuming property_name is the field in sold_property_table
#         profit = asset.profit  # Assuming profit is the field in sold_property_table
        
#         # Fetch shareholders and their contributions from the Asset DocType
#         shareholders = frappe.get_all(
#             "Shareholder Property",
#             filters={"parent": property_name},  # Fetch shareholders related to the specific property
#             fields=["shareholder", "contribution"]
#         )
        
#         # Calculate each shareholder's share of the profit
#         shareholder_shares = []
#         for shareholder in shareholders:
#             # Ensure contribution is not None to avoid errors
#             if shareholder.contribution is not None:
#                 share_amount = (profit * shareholder.contribution) / 100
#                 shareholder_shares.append(
#                     f"{shareholder.shareholder}: {share_amount:.2f}"
#                 )
#             else:
#                 shareholder_shares.append(
#                     f"{shareholder.shareholder}: No contribution recorded"
#                 )
        
#         # Add the calculated shares to the respective property row in sold_property_table
#         asset.shareholder_shares = "\n".join(shareholder_shares)  # Assuming shareholder_shares is a field in the child table
    
#     # # Save the document after updating the rows
#     # doc.save()

# @frappe.whitelist()
# def after_save_sold_property_summary(doc, method):
#     # Fetch the selected shareholder and property
#     selected_shareholder = doc.shareholder
#     main_property = doc.property

#     total_profit = 0  # Initialize total profit for the shareholder

#     # Iterate through each property in the sold_property_table
#     for asset in doc.sold_property_table:
#         property_name = asset.property_name
#         profit = asset.profit

#         # Fetch the shareholder's contribution for the specific property
#         shareholder_contribution = frappe.db.get_value(
#             "Shareholder Property",
#             {"parent": property_name, "shareholder": selected_shareholder},
#             "contribution"
#         )

#         # Calculate profit for the selected shareholder
#         shareholder_profit = 0
#         if shareholder_contribution:
#             shareholder_profit = (profit * shareholder_contribution) / 100
#             total_profit += shareholder_profit

#         # Update the child table with the calculated shareholder profit
#         frappe.db.set_value(
#             "Sold Property Details",
#             asset.name,
#             {
#                 "shareholder_profit": shareholder_profit
#             }
#         )

#     # Update the total profit for the shareholder in the parent DocType
#     doc.total_shareholder_profit = total_profit
#     frappe.db.set_value("Sold Property Summary", doc.name, "total_shareholder_profit", total_profit)


@frappe.whitelist()
def after_save_sold_property_summary(doc, method):
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
