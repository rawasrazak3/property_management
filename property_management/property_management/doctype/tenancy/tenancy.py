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
def create_invoice(tenant, prt, prt_name, amt, custom_tenancy_id):
    items = [
        {"item_code": "Sujlam", "qty": 1, "rate": 100},
        
    ]
    ass_item = frappe.db.get_value('Item', {'asset': prt}, ['item_code'])
    doc = frappe.new_doc("Sales Invoice")
    doc.customer = tenant
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
def create_sales_invoice(customer, commission, tenancy_id, child_row_name):
    # Create a new Sales Invoice document
    invoice = frappe.get_doc({
        'doctype': 'Sales Invoice',
        'customer': customer,
        'tenancy_reference': tenancy_id,  # Custom field in Sales Invoice for tenancy reference
        'items': [{
            'item_code': 'Commission',  # The fixed item name
            'qty': 1,
            'rate': commission,  # Apply the commission amount
            'description': f'Commission for schedule {child_row_name}'
        }]
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
