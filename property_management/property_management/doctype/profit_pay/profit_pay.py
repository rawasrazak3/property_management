# # Copyright (c) 2025, Ketan Patel and contributors
# # For license information, please see license.txt

# import frappe
# from frappe.model.document import Document


# class ProfitPay(Document):
# 	pass
# # In your custom app's Python file
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

# @frappe.whitelist()
# def after_save_profit_pay(doc, method):
#     # Ensure all calculations are dynamic and save changes properly
#     selected_shareholder = doc.shareholder
#     main_property = doc.property
#     total_profit = 0  # Initialize total profit
#     total_profits = 0
#     total_contribution = 0
#     contribution = doc.contribution

#     # Iterate through each row in the child table
#     for asset in doc.sold_property_table:
#         property_name = asset.property_name
#         profit = asset.profit
#         # Accumulate the total profit
#         if profit:
#             total_profits += profit

#         # Fetch shareholder contribution for the specific property
#         shareholder_contribution = frappe.db.get_value(
#             "Shareholder Property",
#             {"parent": property_name, "shareholder": selected_shareholder},
#             "contribution"
#         )

#         # Calculate shareholder profit for the current property
#         shareholder_profit = 0
#         if shareholder_contribution:
#             shareholder_profit = (profit * shareholder_contribution) / 100
#             total_profit += shareholder_profit

#         # Update the child row's shareholder_profit field
#         asset.shareholder_profit = shareholder_profit

#     # Update the total profit for the selected shareholder
#     doc.total_shareholder_profit = total_profit
#     doc.total_profit = total_profits
#     doc.total_contribution = total_profit + contribution

# # from decimal import Decimal, ROUND_HALF_UP

# # @frappe.whitelist()
# # def after_save_profit_pay(doc, method):
# #     # Ensure all calculations are dynamic and save changes properly
# #     selected_shareholder = doc.shareholder
# #     main_property = doc.property
# #     total_profit = Decimal(0)  # Initialize total profit as Decimal
# #     total_profits = Decimal(0)
# #     total_contribution = Decimal(0)
# #     contribution = Decimal(doc.contribution)  # Ensure contribution is a Decimal

# #     # Iterate through each row in the child table
# #     for asset in doc.sold_property_table:
# #         property_name = asset.property_name
# #         profit = Decimal(asset.profit) if asset.profit else Decimal(0)  # Ensure profit is Decimal
# #         # Accumulate the total profit
# #         total_profits += profit

# #         # Fetch shareholder contribution for the specific property
# #         shareholder_contribution = frappe.db.get_value(
# #             "Shareholder Property",
# #             {"parent": property_name, "shareholder": selected_shareholder},
# #             "contribution"
# #         )

# #         # If shareholder contribution exists, calculate shareholder profit
# #         if shareholder_contribution:
# #             shareholder_contribution = Decimal(shareholder_contribution)  # Ensure it's a Decimal
# #             shareholder_profit = (profit * shareholder_contribution) / Decimal(100)
# #             total_profit += shareholder_profit
# #             asset.shareholder_profit = shareholder_profit

# #     # Update the total profit for the selected shareholder
# #     doc.total_shareholder_profit = total_profit.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
# #     doc.total_profit = total_profits.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
# #     doc.total_contribution = (total_profit + contribution).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

# #     # Log the final totals for debugging
# #     frappe.logger().debug(f"Total Shareholder Profit: {doc.total_shareholder_profit}, Total Profit: {doc.total_profit}, Total Contribution: {doc.total_contribution}")

    
# @frappe.whitelist()
# def create_profit_payout_journal(profit_pay_id, mode_of_payment):
#     # Fetch the default account for the selected Mode of Payment
#     mode_of_payment_account = frappe.db.get_value(
#         "Mode of Payment Account",
#         {"parent": mode_of_payment},
#         "default_account"
#     )

#     if not mode_of_payment_account:
#         frappe.throw(f"No default account found for Mode of Payment: {mode_of_payment}")

#     # Fetch the Profit Pay document
#     profit_pay_doc = frappe.get_doc('Profit Pay', profit_pay_id)
#     asset = frappe.get_doc('Asset', profit_pay_doc.property)

#     # Calculate total shareholder profit
#     total_shareholder_profit = profit_pay_doc.total_shareholder_profit
#     # for sold_property in profit_pay_doc.sold_properties:
#     #     total_shareholder_profit += sold_property.shareholder_profit

#     # if total_shareholder_profit <= 0:
#     #     frappe.throw("Total shareholder profit must be greater than zero.")

#     # Prepare the Journal Entry
#     journal_entry = frappe.new_doc('Journal Entry')
#     journal_entry.voucher_type = 'Journal Entry'
#     journal_entry.posting_date = frappe.utils.nowdate()
#     journal_entry.company = asset.company
#     journal_entry.user_remark = f'Profit Payout for Asset: {asset.name}'

#     # Add Credit Entry (Mode of Payment Account)
#     journal_entry.append('accounts', {
#         'account': mode_of_payment_account,
#         'credit_in_account_currency': total_shareholder_profit,
#         'credit': total_shareholder_profit
#     })

#     # Add Debit Entries for each shareholder based on properties
#     for sold_property in profit_pay_doc.sold_property_table:
#         contribution_amount = sold_property.shareholder_profit
#         ref_name =  sold_property.property_name
#         if contribution_amount > 0:
#             journal_entry.append('accounts', {
#                 'account': profit_pay_doc.shareholder_account,
#                 'debit_in_account_currency': contribution_amount,
#                 'debit': contribution_amount,
#                 'party_type': 'Shareholder',
#                 'party': profit_pay_doc.shareholder,
#                 'project': asset.custom_project,
#                 'reference_type': 'Asset',
#                 'reference_name': sold_property.property_name
                
#             })

#             # Mark the profit as paid in the Asset DocType
#             asset_doc = frappe.get_doc('Asset', sold_property.property_name)
#             # asset_doc.db_set('custom_profit_paid', 1)

#     # Save and submit the Journal Entry
#     journal_entry.insert()
#     # journal_entry.submit()

#     # Commit changes to ensure data consistency
#     frappe.db.commit()

#     return journal_entry.name

# # from decimal import Decimal, ROUND_HALF_UP

# # @frappe.whitelist()
# # def create_profit_payout_journal(profit_pay_id, mode_of_payment):
# #     # Fetch the default account for the selected Mode of Payment
# #     mode_of_payment_account = frappe.db.get_value(
# #         "Mode of Payment Account",
# #         {"parent": mode_of_payment},
# #         "default_account"
# #     )

# #     if not mode_of_payment_account:
# #         frappe.throw(f"No default account found for Mode of Payment: {mode_of_payment}")

# #     # Fetch the Profit Pay document
# #     profit_pay_doc = frappe.get_doc('Profit Pay', profit_pay_id)
# #     asset = frappe.get_doc('Asset', profit_pay_doc.property)

# #     # Calculate total shareholder profit and round to 2 decimal places using Decimal
# #     total_shareholder_profit = Decimal(str(profit_pay_doc.total_shareholder_profit)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

# #     # Prepare the Journal Entry
# #     journal_entry = frappe.new_doc('Journal Entry')
# #     journal_entry.voucher_type = 'Journal Entry'
# #     journal_entry.posting_date = frappe.utils.nowdate()
# #     journal_entry.company = asset.company
# #     journal_entry.user_remark = f'Profit Payout for Asset: {asset.name}'

# #     # Add Credit Entry (Mode of Payment Account)
# #     journal_entry.append('accounts', {
# #         'account': mode_of_payment_account,
# #         'credit_in_account_currency': total_shareholder_profit,
# #         'credit': total_shareholder_profit
# #     })

# #     # Add Debit Entries for each shareholder based on properties
# #     total_debit = Decimal('0.00')  # Variable to track total debit

# #     for sold_property in profit_pay_doc.sold_property_table:
# #         contribution_amount = Decimal(str(sold_property.shareholder_profit)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)  # Round to 2 decimal places
# #         ref_name = sold_property.property_name
        
# #         if contribution_amount > 0:
# #             # Check if a similar entry already exists in any other journal entry
# #             existing_entry = frappe.db.sql("""
# #                 SELECT je.name
# #                 FROM `tabJournal Entry` je
# #                 INNER JOIN `tabJournal Entry Account` jea ON je.name = jea.parent
# #                 WHERE je.docstatus = 1
# #                   AND jea.party_type = 'Shareholder'
# #                   AND jea.party = %s
# #                   AND jea.reference_type = 'Asset'
# #                   AND jea.reference_name = %s
# #                   AND je.name != %s
# #                 LIMIT 1
# #             """, (profit_pay_doc.shareholder, sold_property.property_name, journal_entry.name))

# #             if not existing_entry:
# #                 journal_entry.append('accounts', {
# #                     'account': profit_pay_doc.shareholder_account,
# #                     'debit_in_account_currency': contribution_amount,
# #                     'debit': contribution_amount,
# #                     'party_type': 'Shareholder',
# #                     'party': profit_pay_doc.shareholder,
# #                     'project': asset.custom_project,
# #                     'reference_type': 'Asset',
# #                     'reference_name': sold_property.property_name
# #                 })

# #                 # Add to total debit
# #                 total_debit += contribution_amount

# #                 # Mark the profit as paid in the Asset DocType
# #                 asset_doc = frappe.get_doc('Asset', sold_property.property_name)
# #                 # asset_doc.db_set('custom_profit_paid', 1)

# #     # Round total debit and credit to two decimal places for comparison
# #     rounded_total_debit = total_debit.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
# #     rounded_total_credit = total_shareholder_profit.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

# #     # Debugging logs to check the values before comparison
# #     frappe.logger().debug(f"Rounded Total Debit: {rounded_total_debit}, Rounded Total Credit: {rounded_total_credit}")

# #     # Check if the total debit matches the total credit with a tolerance of 0.01
# #     difference = abs(rounded_total_debit - rounded_total_credit)
# #     tolerance = Decimal('0.01')

# #     # If difference is greater than tolerance, log the difference and adjust
# #     if difference > tolerance:
# #         frappe.logger().debug(f"Difference is too large: {difference}. Adjusting...")

# #         # We adjust the total to match within the tolerance
# #         if rounded_total_debit > rounded_total_credit:
# #             rounded_total_credit = rounded_total_debit
# #         else:
# #             rounded_total_debit = rounded_total_credit

# #         # Log adjusted totals for debugging
# #         frappe.logger().debug(f"Adjusted Total Debit: {rounded_total_debit}, Adjusted Total Credit: {rounded_total_credit}")

# #     # Final check for exact equality
# #     if rounded_total_debit != rounded_total_credit:
# #         frappe.logger().debug(f"Adjusted Total Debit: {rounded_total_debit}, Adjusted Total Credit: {rounded_total_credit}")
# #         frappe.throw(f"Total Debit must be equal to Total Credit. Diference is {rounded_total_debit - rounded_total_credit:.2f}")

# #     # Save and submit the Journal Entry
# #     journal_entry.insert()
# #     # journal_entry.submit()

# #     # Commit changes to ensure data consistency
# #     frappe.db.commit()

# #     return journal_entry.name


# @frappe.whitelist()
# def fetch_filtered_asset(property_id, shareholder_name, properties_list, limit_page_length=100):
#     if not property_id:
#         frappe.throw("Property ID is required.")
#     if not shareholder_name:
#         frappe.throw("Shareholder Name is required.")
#     if not properties_list:
#         frappe.log_error(f"Properties List received: {properties_list}", "Properties List Error")
#         frappe.throw("Properties List is required and must be a non-empty list.")

#     # Safeguard against unreasonable limit values
#     limit_page_length = min(int(limit_page_length), 1000)  # Restrict maximum limit

#     try:
#         # Fetch existing Profit Pay entries for the same property and shareholder
#         profit_pay_query = """
#             SELECT 
#                 sp.property_name AS existing_property_id
#             FROM 
#                 `tabProfit Pay` pp
#             LEFT JOIN 
#                 `tabSold Property Details` sp ON sp.parent = pp.name
#             WHERE 
#                 pp.property = %(property_id)s
#                 AND pp.shareholder = %(shareholder_name)s
#         """
#         existing_entries = frappe.db.sql(
#             profit_pay_query, 
#             {"property_id": property_id, "shareholder_name": shareholder_name}, 
#             as_dict=True
#         )

#         # Extract existing property IDs
#         existing_property_ids = {
#             entry['existing_property_id'] for entry in existing_entries if entry.get('existing_property_id')
#         }

#         # Filter out properties already included in other Profit Pay entries
#         unique_properties = []
#         removed_properties = []  # To store removed properties for logging/debugging

#         for property in properties_list:
#             if isinstance(property, str):
#                       current_property_id = property
#             else:
#                    current_property_id = property.get('property_name')
#             if current_property_id in existing_property_ids:
#                 removed_properties.append(property)  # Capture removed properties
#             else:
#                 unique_properties.append(property)


#         # Log the removed entries
#         if removed_properties:
#             frappe.logger().info(f"Removed {len(removed_properties)} duplicate properties: {removed_properties}")

#         # Return the filtered list of unique properties
#         return unique_properties

#     except Exception as e:
#         frappe.log_error(message=str(e), title="Fetch Filtered Asset Error")
#         return []








