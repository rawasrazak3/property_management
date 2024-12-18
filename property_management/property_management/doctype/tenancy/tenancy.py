# Copyright (c) 2024, Ketan Patel and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class Tenancy(Document):
	pass
def tenant_schedule(doc, event):
    for d in doc.get('tenant_schedule'):
        if d.schedule_date:
            event = frappe.db.get_list('Event',filters={'tenant_schedule_id': d.tenant_schedule_id},fields=['tenant_schedule_id'],as_list=True)
            if not event:
                new_event = frappe.get_doc(dict(
                    doctype = 'Event',
                    starts_on = d.schedule_date,
                    subject = doc.asset_name +' - '+ d.schedule_date,
                    asset_id = doc.asset,
                    tenant_schedule_id = d.tenant_schedule_id
                ))
                new_event.append('event_participants', {
                    'reference_doctype': "Asset", 'reference_docname': doc.asset
                    })
                new_event.append('event_participants', {
                    'reference_doctype': "Tenancy", 'reference_docname': doc.name
                    })
                new_event.save()

@frappe.whitelist()
def create_invoice(tenant, schedule_date, prt, prt_name, amt, custom_tenancy_id):
    items = [
        {"item_code": "Sujlam", "qty": 1, "rate": 100},
        
    ]
    ass_item = frappe.db.get_value('Item', {'asset': prt}, ['item_code'])
    doc = frappe.new_doc("Sales Invoice")
    doc.customer = tenant
    doc.set_posting_time = 1,
    doc.posting_date = schedule_date
    doc.property = prt  
    doc.property_name = prt_name
    doc.custom_tenancy_id = custom_tenancy_id
    for item in items:
        doc.append("items", {
            "item_code": ass_item,
            "qty": 1,
            "rate": amt,
            "asset": prt
        })
    doc.insert(ignore_permissions=True)
    doc.submit()
    frappe.db.commit()
    return doc.name  

@frappe.whitelist()
def create_invoice_landlord(landlord, prt, prt_name, amt, custom_tenancy_id):
    items = [
        {"item_code": "Sujlam", "qty": 1, "rate": 100},
        
    ]
    ass_item = frappe.db.get_value('Item', {'asset': prt}, ['item_code'])
    doc = frappe.new_doc("Sales Invoice")
    doc.customer = landlord
    doc.property = prt  
    doc.property_name = prt_name
    doc.custom_tenancy_id = custom_tenancy_id
    for item in items:
        doc.append("items", {
            "item_code": ass_item,
            "qty": 1,
            "rate": amt,
            "asset": prt
        })
    doc.insert(ignore_permissions=True)
    doc.submit()
    frappe.db.commit()
    return doc.name  

import frappe

@frappe.whitelist()
def create_paymententry(doc, mode_of_payment, invoice_name, party, posting_date, payment_amount, paid_amount, received_amount, reference_no, paid_to, schedule_date, invoice_ref):
    if invoice_name:
        # Step 1: Insert the Payment Entry without references
        payment_entry = frappe.get_doc(dict(
            doctype = 'Payment Entry',
            payment_type = 'Receive',
            party_type = 'Customer',
            party = party,
            mode_of_payment = mode_of_payment,
            reference_no = reference_no,
            reference_date = schedule_date,
            posting_date = posting_date,
            custom_schedule_date = schedule_date,
            custom_invoice_ref = invoice_ref,
            payment_amount = abs(float(payment_amount)),
            paid_amount = abs(float(paid_amount)),
            received_amount = abs(float(received_amount)),
            paid_to = paid_to
        ))
        payment_entry.insert(ignore_permissions=True)
        frappe.db.commit()

        # Step 2: Fetch the inserted Payment Entry and add references
        payment_entry = frappe.get_doc('Payment Entry', payment_entry.name)
        payment_entry.append('references', {
            'reference_doctype': 'Sales Invoice',
            'reference_name': invoice_name,
            'total_amount': abs(float(payment_amount)),
            'outstanding_amount': abs(float(payment_amount)),
            'allocated_amount': abs(float(payment_amount))
        })
        payment_entry.save()  # Update the document
        frappe.db.commit()

    return payment_entry.name



@frappe.whitelist()
def create_paymententry_landlord(doc, invoice_name, party, payment_amount, paid_amount,received_amount, paid_to, schedule_date,invoice_ref):
    if invoice_name:
            payment_entry = frappe.get_doc(dict(
                doctype = 'Payment Entry',
                payment_type = 'Receive',
                party_type = 'Customer',
                party = party,
                posting_date = schedule_date,
                custom_schedule_date = schedule_date,
                custom_invoice_ref = invoice_ref,
                payment_amount = abs(float(payment_amount)),
                paid_amount = abs(float(paid_amount)),
                received_amount = abs(float(received_amount)),
                paid_to = paid_to
            ))
            payment_entry.insert()
            # payment_entry.submit()
            frappe.db.commit()
    return payment_entry.name

    
@frappe.whitelist()
def create_purchase_invoice(supplier, prt, prt_name, net_amount, custom_tenancy_id):
    # Example items, this can be modified based on your requirement
    items = [
        {"item_code": "Sujlam", "qty": 1, "rate": 100},
    ]
    
    # Fetch item associated with the asset
    ass_item = frappe.db.get_value('Item', {'asset': prt}, ['item_code'])
    
    # Create the Purchase Invoice
    doc = frappe.new_doc("Purchase Invoice")
    doc.supplier = supplier
    doc.property = prt
    doc.property_name = prt_name
    doc.custom_tenancy_id = custom_tenancy_id
    
    # Add items to the Purchase Invoice
    for item in items:
        doc.append("items", {
            "item_code": ass_item,
            "qty": 1,
            "rate": net_amount,  # Apply the calculated net_amount here
            "asset": prt
        })
    
    # Insert and submit the document
    doc.insert(ignore_permissions=True)
    doc.submit()
    frappe.db.commit()
    
    return doc.name


@frappe.whitelist()
def create_purchase_payment_entry(doc, supplier, paid_from, purchase_invoice, schedule_date,reference_no, invoice_ref):
    # Step 1: Fetch the net_amount from the Purchase Invoice
    net_amount = frappe.db.get_value('Purchase Invoice', purchase_invoice, 'net_total')

    if not net_amount:
        frappe.throw(f"Unable to find net amount for Purchase Invoice {purchase_invoice}")

    if purchase_invoice:
        # Step 2: Create Payment Entry for Purchase Invoice (using net_amount for allocated_amount and paid_amount)
        payment_entry = frappe.get_doc(dict(
            doctype = 'Payment Entry',
            payment_type = 'Pay',
            party_type = 'Supplier',
            party = supplier,
            posting_date = schedule_date,
            reference_no = reference_no,
            reference_date = schedule_date,
            custom_schedule_date = schedule_date,
            custom_invoice_ref = invoice_ref,
            paid_amount = abs(float(net_amount)),  # Using net_amount here
            received_amount = abs(float(net_amount)),  # Net amount for payment
            paid_from = paid_from
        ))
        payment_entry.insert()
        frappe.db.commit()

        # Step 3: Append the references to the Purchase Invoice
        payment_entry = frappe.get_doc('Payment Entry', payment_entry.name)
        payment_entry.append('references', {
            'reference_doctype': 'Purchase Invoice',
            'reference_name': purchase_invoice,
            'total_amount': abs(float(net_amount)),  # Using net_amount here
            'outstanding_amount': abs(float(net_amount)),  # Using net_amount here
            'allocated_amount': abs(float(net_amount))  # Using net_amount here
        })
        payment_entry.save()
        frappe.db.commit()

    return payment_entry.name

@frappe.whitelist()
def create_partial_paymententry(doc, invoice_name, party, posting_date, payment_amount, paid_amount, received_amount, reference_no, paid_to, schedule_date, invoice_ref):
    if invoice_name:
        # Step 1: Insert the Payment Entry without references
        payment_entry = frappe.get_doc(dict(
            doctype = 'Payment Entry',
            payment_type = 'Receive',
            party_type = 'Customer',
            party = party,
            reference_no = reference_no,
            reference_date = schedule_date,
            posting_date = posting_date,
            custom_schedule_date = schedule_date,
            custom_invoice_ref = invoice_ref,
            payment_amount = abs(float(payment_amount)),
            paid_amount = abs(float(paid_amount)),
            received_amount = abs(float(received_amount)),
            paid_to = paid_to
        ))
        payment_entry.insert()
        frappe.db.commit()

        # Step 2: Fetch the inserted Payment Entry and add references
        payment_entry = frappe.get_doc('Payment Entry', payment_entry.name)
        payment_entry.append('references', {
            'reference_doctype': 'Sales Invoice',
            'reference_name': invoice_name,
            'total_amount': abs(float(payment_amount)),
            'outstanding_amount': abs(float(payment_amount)),
            'allocated_amount': abs(float(payment_amount))
        })
        payment_entry.save()
        payment_entry.submit()
        frappe.db.commit()

    return payment_entry.name

@frappe.whitelist()
def create_sales_invoice(customer, commission, one_time_commission, tenancy_id, child_row_name):
    # Ensure commission and one_time_commission are numeric
    commission = float(commission) if commission else 0
    one_time_commission = float(one_time_commission) if one_time_commission else 0

    # Create a new Sales Invoice document
    invoice = frappe.get_doc({
        'doctype': 'Sales Invoice',
        'customer': customer,
        'tenancy_reference': tenancy_id,  # Custom field in Sales Invoice for tenancy reference
        'items': [
            {
                'item_code': 'Management Fees',  # The first item for commission
                'qty': 1,
                'rate': commission,  # Apply the commission amount
                'description': f'Management Fees for schedule {child_row_name}'
            }
        ]
    })

    # If one_time_commission exists, add a second item for it
    if one_time_commission > 0:
        invoice.append('items', {
            'item_code': 'Renting Fees',  # The second item for one-time commission
            'qty': 1,
            'rate': one_time_commission,  # Apply the one-time commission amount
            'description': f'Renting Fees for schedule {child_row_name}'
        })

    # Add a tax row to the taxes table with required values
    invoice.append('taxes', {
        'charge_type': 'On Net Total',
        'account_head': 'Vat 5% - ABR',
        'rate': 5.0,  # Assuming VAT is 5%
        'description': 'VAT 5%'
    })

    # Insert and submit the Sales Invoice
    invoice.insert(ignore_permissions=True)
    invoice.submit()
    frappe.db.commit()

    return invoice.name



@frappe.whitelist()
def create_paymententry(doc, invoice_name, party, posting_date, payment_amount, paid_amount, received_amount, reference_no, paid_to, schedule_date, invoice_ref):
    if invoice_name:
        # Step 1: Insert the Payment Entry without references
        payment_entry = frappe.get_doc(dict(
            doctype = 'Payment Entry',
            payment_type = 'Receive',
            party_type = 'Customer',
            party = party,
            reference_no = reference_no,
            reference_date = schedule_date,
            posting_date = posting_date,
            custom_schedule_date = schedule_date,
            custom_invoice_ref = invoice_ref,
            payment_amount = abs(float(payment_amount)),
            paid_amount = abs(float(paid_amount)),
            received_amount = abs(float(received_amount)),
            paid_to = paid_to
        ))
        payment_entry.insert()
        frappe.db.commit()

        # Step 2: Fetch the inserted Payment Entry and add references
        payment_entry = frappe.get_doc('Payment Entry', payment_entry.name)
        payment_entry.append('references', {
            'reference_doctype': 'Sales Invoice',
            'reference_name': invoice_name,
            'total_amount': abs(float(payment_amount)),
            'outstanding_amount': abs(float(payment_amount)),
            'allocated_amount': abs(float(payment_amount))
        })
        payment_entry.save()  # Update the document
        frappe.db.commit()

    return payment_entry.name

@frappe.whitelist()
def get_default_account(mode_of_payment):
    # Fetch the default account linked to the mode of payment
    account = frappe.db.get_value('Mode of Payment Account', {'parent': mode_of_payment}, 'default_account')
    return account

import frappe

def before_cancel(doc, method):
    tenancy_id = doc.name

    # Cancel all linked sales invoices where custom_tenancy_id == tenancy_id
    linked_sales_invoices = frappe.get_all('Sales Invoice', filters={'custom_tenancy_id': tenancy_id, 'docstatus': 1})
    for invoice in linked_sales_invoices:
        try:
            # Fetch the Sales Invoice with ignore_permissions
            sales_invoice = frappe.get_doc('Sales Invoice', invoice.name)
            sales_invoice.flags.ignore_permissions = True  # Ignore permissions to allow canceling
            sales_invoice.flags.ignore_links = True  # Ignore linked document validation
            # Cancel the sales invoice
            if sales_invoice.docstatus == 1:
                sales_invoice.cancel()
                frappe.msgprint(f"Sales Invoice {sales_invoice.name} canceled successfully.")
        except Exception as e:
            frappe.throw(f"Error canceling Sales Invoice {sales_invoice.name}: {str(e)}")

    # Cancel all linked purchase invoices where custom_tenancy_id == tenancy_id
    linked_purchase_invoices = frappe.get_all('Purchase Invoice', filters={'custom_tenancy_id': tenancy_id, 'docstatus': 1})
    for invoice in linked_purchase_invoices:
        try:
            # Fetch the Purchase Invoice with ignore_permissions
            purchase_invoice = frappe.get_doc('Purchase Invoice', invoice.name)
            purchase_invoice.flags.ignore_permissions = True  # Ignore permissions to allow canceling
            purchase_invoice.flags.ignore_links = True  # Ignore linked document validation
            # Cancel the purchase invoice
            if purchase_invoice.docstatus == 1:
                purchase_invoice.cancel()
                frappe.msgprint(f"Purchase Invoice {purchase_invoice.name} canceled successfully.")
        except Exception as e:
            frappe.throw(f"Error canceling Purchase Invoice {purchase_invoice.name}: {str(e)}")

@frappe.whitelist()
def create_contract_on_tenancy_save(self, method=None):
    # Check if the custom_contract field is empty
    if not self.custom_contract:
        # Create a new Contract
        contract = frappe.new_doc('Contract')
        contract.party_type = 'Customer'
        contract.party_name = self.tenant  # Assuming custom_tenant is the field holding the party name
        contract.custom_property_name = self.asset  # Assuming the field holding the property name is 'property'
        contract.start_date = self.start_date  # Replace with the correct field name for tenancy start date
        contract.end_date = self.end_date  # Replace with the correct field name for tenancy end date
        property_name = self.asset  # Adjust if your field for property is named differently
        start_date = frappe.utils.formatdate(self.start_date)
        end_date = frappe.utils.formatdate(self.end_date)
        
        # Create a contract term description
        contract.contract_terms = f"Contract for {property_name} from {start_date} to {end_date}."
        
        # Save the Contract
        contract.insert()
        contract.submit()
        frappe.db.commit()

        # Update the custom_contract field in Tenancy with the created Contract ID
        self.db_set('custom_contract', contract.name)
