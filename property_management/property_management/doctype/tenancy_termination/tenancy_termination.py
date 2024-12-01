# Copyright (c) 2024, Ketan Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime

class TenancyTermination(Document):
	pass

@frappe.whitelist()
def calculate_outstanding_rent(tenancy_name,tenancy_end_date):
    outstanding_rent = 0
    tenancy = frappe.get_doc('Tenancy', tenancy_name)
    tenancy_end_date = datetime.strptime(tenancy_end_date, '%Y-%m-%d').date()
    for entry in tenancy.tenant_schedule:
        # Convert frappe.utils.nowdate() to a datetime.date object
        
        current_date = datetime.strptime(frappe.utils.nowdate(), '%Y-%m-%d').date()
        
        # Compare dates
        if not entry.is_paid and entry.schedule_date <= tenancy_end_date:
            outstanding_rent += entry.amount

    return outstanding_rent

@frappe.whitelist()
def fetch_tax_data(template_name):
    tax_data = frappe.get_value('Item Tax Template Detail',{'parent': template_name},'tax_rate')
    return tax_data

@frappe.whitelist()
def create_journal_entry(doc, method):
    mode_of_payment_account = frappe.db.get_value(
            "Mode of Payment Account",
            {"parent": doc.mode_of_payment,"company":doc.company_name},
            "default_account"
        )
        
    if not mode_of_payment_account:
        frappe.throw(f"No default account found for Mode of Payment: {doc.mode_of_payment}")

    #create journal entry
    journal_entry = frappe.new_doc("Journal Entry")
    journal_entry.posting_date = frappe.utils.nowdate()
    journal_entry.company = doc.company_name
    journal_entry.user_remark = f"Journal Entry for Tenancy Termination {doc.name}"
    tenant_account = frappe.get_value('Company', doc.company_name, 'default_receivable_account') or "Debtors"
    if doc.amount_payable > 0:
        journal_entry.append("accounts", {
            "account": mode_of_payment_account,  # Replace with the mode of payment's account
            "credit_in_account_currency": doc.amount_payable,
            "credit": doc.amount_payable,
            'reference_type': 'Asset',
            'reference_name': doc.property
        })
        journal_entry.append("accounts", {
            "account": tenant_account,  # Replace with the customer's account
            "debit_in_account_currency": doc.amount_payable,
            "debit": doc.amount_payable,
            'party_type': 'Customer',
            'party': doc.tenant,
            'reference_type': 'Asset',
            'reference_name': doc.property
        })
    elif doc.amount_receivable > 0:
        journal_entry.append("accounts", {
            "account": mode_of_payment_account,  # Replace with the mode of payment's account
            "debit_in_account_currency": doc.amount_receivable,
            "debit": doc.amount_receivable,
            'reference_type': 'Asset',
            'reference_name': doc.property
        })
        journal_entry.append("accounts", {
            "account": tenant_account,  # Replace with the customer's account
            "credit_in_account_currency": doc.amount_receivable,
            "credit": doc.amount_receivable,
            'party_type': 'Customer',
            'party': doc.tenant,
            'reference_type': 'Asset',
            'reference_name': doc.property
        })
    
    journal_entry.save()
    
    # Set the Journal Entry ID in the tenancy termination
    doc.journal_entry_id = journal_entry.name

@frappe.whitelist()
def manage_property_on_termination(doc, method):
    # Fetch the linked property
    if not doc.property:
        frappe.throw("No property linked to the Tenancy Termination.")
    
    # Get the property details
    property_doc = frappe.get_doc("Asset", doc.property)

    # Create a duplicate property entry
    new_property = frappe.new_doc("Asset")
    new_property.update({
        "item_code": property_doc.item_code,
        "asset_name": property_doc.asset_name,
        "asset_category": property_doc.asset_category,
        "item_name": property_doc.item_name,
        "location": property_doc.location,
        "custom_property_type": property_doc.custom_property_type,
        "ground_rent": property_doc.ground_rent,
        "latitude": property_doc.latitude,
        "longitude": property_doc.longitude,
        "no_of_towers":property_doc.no_of_towers,
        "custom_no_of_floor":property_doc.custom_no_of_floor,
        "custom_floor_no":property_doc.custom_floor_no,
        "gfa_sqft":property_doc.gfa_sqft,
        "gfa_m":property_doc.gfa_m,
        "unit_price": property_doc.unit_price,
        "total_price": property_doc.total_price,
        "available_for_use_date": property_doc.available_for_use_date,
        "is_existing_asset":1,
        "gross_purchase_amount": property_doc.gross_purchase_amount,
        "total_asset_cost": property_doc.total_asset_cost,
        "asset_quantity": property_doc.asset_quantity,
        "additional_asset_cost": property_doc.additional_asset_cost,
        "custom_actual_property_amount": property_doc.custom_actual_property_amount,
        "custom_total_expenses": property_doc.asset_quantity,
        "custom_wilayat": property_doc.custom_wilayat,
        "custom_property_unit": property_doc.custom_property_unit,
        "custom_property_subunit": property_doc.custom_property_subunit,
        "asset_owner": property_doc.asset_owner,
        "custom_property_owner": property_doc.custom_property_owner,
        "supplier": property_doc.supplier,
        "custom_commission": property_doc.custom_commission,
        "custom_one_time_commission": property_doc.custom_one_time_commission,
        "custodian": property_doc.custodian,
        "department": property_doc.department,
        "purchase_date": property_doc.purchase_date,
        "furnishing": property_doc.furnishing,
        "bedrooms": property_doc.bedrooms,
        "bathrooms": property_doc.bathrooms,
        "parking": property_doc.parking,
        "facing": property_doc.facing,
        "rent_type": property_doc.rent_type,
        # "calculate_depreciation": property_doc.calculate_depreciation,
        
        # Add more fields as necessary from the original Property DocType
    })

    # Set the new property status from the tenancy termination
    new_property.property_status = doc.property_status
    new_property.insert()

    # Close the current property by updating its status
    property_doc.property_status = "Closed"
    property_doc.save()

    # Add a note in the tenancy termination about the new property created
    doc.new_property = new_property.name

@frappe.whitelist()
def create_invoice_on_tenency_exit(doc, method):
    if doc.apply_charge_to_tenant:
        if not doc.amount:
            frappe.throw("No Charge is Added")
        invoice=frappe.new_doc('Sales Invoice')
        invoice.posting_date = frappe.utils.nowdate()
        invoice.company = doc.company_name
        invoice.customer = doc.tenant
        invoice.tenancy_reference = doc.tenancy
        invoice.description = f"Invoice for Charge in Tenancy Termination {doc.name}"
        invoice.append('items', {
            'item_code': 'Charge Against Tenancy',  # The second item for one-time commission
            'qty': 1,
            'rate': doc.amount,  # Apply the charge amount
            'description': f"Invoice for Charge in Tenancy Termination {doc.name}"
        })
        if doc.vat:
            invoice.append('taxes', {
            'charge_type': 'On Net Total',
            'account_head': 'Vat 5% - ABR',
            'rate': 5.0,  # Assuming VAT is 5%
            'description': 'VAT 5%'
            })

        invoice.insert(ignore_permissions=True)
        invoice.submit()
        frappe.db.commit()
        doc.sales_invoice_id = invoice.name