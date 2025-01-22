# Copyright (c) 2024, Ketan Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, date_diff, getdate



class TenancyBulkPayment(Document):
	pass

# @frappe.whitelist()
# def fetch_outstanding_rent(from_date, to_date):
# 	if not from_date or not to_date:
# 		frappe.throw("Please provide both From Date and To Date.")

# 	# Convert dates to ensure proper comparison
# 	from_date = getdate(from_date)
# 	to_date = getdate(to_date)

# 	# Fetch tenancies where the given date range overlaps with the tenancy period
# 	tenancies = frappe.get_all(
# 		"Tenancy",
# 		filters={
# 			"custom_status": "Active",
# 			"start_date": ["<=", to_date],
# 			"end_date": [">=", from_date]
# 		},
# 		fields=["name", "asset", "tenant", "start_date", "end_date"]
# 	)

# 	# Prepare a dictionary to hold aggregated rent data
# 	outstanding_rent_data = {}

# 	for tenancy in tenancies:
# 		# Fetch tenant schedules within the adjusted date range
# 		tenant_schedules = frappe.get_all(
# 			"Tenant Schedule",
# 			filters={
# 				"parent": tenancy.name,
# 				"schedule_date": ["between", [from_date, to_date]],
# 				"is_paid": 0
# 			},
# 			fields=["amount"]
# 		)

# 		# Calculate outstanding for the tenancy
# 		outstanding_amount = sum(flt(schedule["amount"]) for schedule in tenant_schedules)

# 		if outstanding_amount > 0:
# 			# Append data to the results
# 			property = tenancy.asset
# 			tenant = tenancy.tenant
# 			if (property, tenant) not in outstanding_rent_data:
# 				outstanding_rent_data[(property, tenant)] = {
# 					"property": property,
# 					"tenant": tenant,
# 					# "total_rent_due": 0,
# 					# "total_paid": 0,
# 					"outstanding_amount": 0
# 				}

# 			outstanding_rent_data[(property, tenant)]["outstanding_amount"] += outstanding_amount

# 	# Convert dictionary values to a list for easier usage
# 	return list(outstanding_rent_data.values())

@frappe.whitelist()
def fetch_outstanding_rent(from_date, to_date):
    if not from_date or not to_date:
        frappe.throw("Please provide both From Date and To Date.")

    # Convert dates to ensure proper comparison
    from_date = getdate(from_date)
    to_date = getdate(to_date)

    # Fetch tenancies where the given date range overlaps with the tenancy period
    tenancies = frappe.get_all(
        "Tenancy",
        filters={
            "custom_status": "Active",
            "start_date": ["<=", to_date],
            "end_date": [">=", from_date]
        },
        fields=["name", "asset", "tenant", "start_date", "end_date","asset_name"]
    )

    # Prepare a list to hold detailed rent schedule data
    outstanding_rent_data = []

    for tenancy in tenancies:
        # Fetch tenant schedules within the adjusted date range
        tenant_schedules = frappe.get_all(
            "Tenant Schedule",
            filters={
                "parent": tenancy.name,
                "schedule_date": ["between", [from_date, to_date]],
                "is_paid": 0
            },
            fields=["name", "schedule_date", "amount","reference_no","invoice"]
        )

        # Add each schedule as a separate entry in the results
        for schedule in tenant_schedules:
            pe_doc = frappe.get_all(
                "Payment Entry",
                filters={
                    "custom_invoice_ref": schedule.invoice
				},
                fields=["name",]
            )
            pe_doc_name = pe_doc[0]["name"] if pe_doc else None
            outstanding_rent_data.append({
                "property": tenancy.asset,
                "tenant": tenancy.tenant,
                "tenancy": tenancy.name,
                "tenant_schedule_id": schedule["name"],
                "schedule_date": schedule["schedule_date"],
                "outstanding_amount": flt(schedule["amount"]),
                "reference_no": schedule["reference_no"],
                "payment_entry": pe_doc_name,
                "property_name": tenancy.asset_name
            })

    return outstanding_rent_data

@frappe.whitelist()
def fetch_outstanding_rent_by_property(main_property, from_date, to_date):
    if not main_property or not from_date or not to_date:
        frappe.throw("Please provide Main Property, From Date, and To Date.")

    # Convert dates to ensure proper comparison
    from_date = getdate(from_date)
    to_date = getdate(to_date)

    # Fetch assets linked to the main property via the "Against Property" field
    assets = frappe.get_all(
        "Asset",
        filters={"custom_against_property": main_property},
        fields=["name"]
    )
    asset_names = [asset.name for asset in assets]

    # Include the main property in the list of assets
    asset_names.append(main_property)

    if not asset_names:
        frappe.msgprint(f"No properties found under the main property {main_property}.")
        return []

    # Fetch tenancies linked to the filtered assets and within the date range
    tenancies = frappe.get_all(
        "Tenancy",
        filters={
            "custom_status": "Active",
            "asset": ["in", asset_names],
            "start_date": ["<=", to_date],
            "end_date": [">=", from_date]
        },
        fields=["name", "asset", "tenant", "start_date", "end_date","asset_name"]
    )

    # Prepare a list to hold detailed rent schedule data
    outstanding_rent_data = []

    for tenancy in tenancies:
        # Fetch tenant schedules within the adjusted date range
        tenant_schedules = frappe.get_all(
            "Tenant Schedule",
            filters={
                "parent": tenancy.name,
                "schedule_date": ["between", [from_date, to_date]],
                "is_paid": 0
            },
            fields=["name", "schedule_date", "amount", "reference_no", "invoice"]
        )

        # Add each schedule as a separate entry in the results
        for schedule in tenant_schedules:
            pe_doc = frappe.get_all(
                "Payment Entry",
                filters={"custom_invoice_ref": schedule.invoice},
                fields=["name"]
            )
            pe_doc_name = pe_doc[0]["name"] if pe_doc else None
            outstanding_rent_data.append({
                "property": tenancy.asset,
                "property_name": tenancy.asset_name,
                "tenant": tenancy.tenant,
                "tenancy": tenancy.name,
                "tenant_schedule_id": schedule["name"],
                "schedule_date": schedule["schedule_date"],
                "outstanding_amount": flt(schedule["amount"]),
                "reference_no": schedule["reference_no"],
                "payment_entry": pe_doc_name,
            })

    return outstanding_rent_data


@frappe.whitelist()
def submit_payment_and_create_entries(payment_entry,tenancy):
    if not payment_entry:
        frappe.throw(("No existing payment entry provided."))

    # Step 1: Submit the existing payment entry
    submit_existing_payment_entry(payment_entry,tenancy)

    # Step 2: Fetch relevant data from the Tenancy Bulk Payment or related DocType
    payment_details = frappe.get_doc("Payment Entry", payment_entry)
    tenancys = frappe.get_doc("Tenancy", tenancy)
    
    for row in tenancys.tenant_schedule:
        if tenancys.asset_owner == "Supplier":
            create_sales_payment_and_purchase(tenancys, row)
        else:
            create_purchase_payment_entry(tenancys, row)

@frappe.whitelist()
def submit_existing_payment_entry(payment_entry,tenancy):
    """Submit an existing payment entry."""
    try:
        doc = frappe.get_doc("Payment Entry", payment_entry)
        tenancy = frappe.get_doc("Tenancy",tenancy)
        if doc.docstatus == 0:  # Check if it's in Draft
            doc.submit()
            for row in tenancy.tenant_schedule:
                row.is_paid = 1
            frappe.msgprint(("Payment entry {0} submitted successfully.").format(payment_entry))
    except Exception as e:
        frappe.throw(("Failed to submit payment entry"))

@frappe.whitelist()
def create_sales_payment_and_purchase(doc, row):
    """Create sales and purchase entries for a tenancy payment."""
    purchase_invoice_id = create_purchase_invoice(doc, row)
    row.purchase_invoice = purchase_invoice_id

    if purchase_invoice_id:
        frappe.db.commit()

    sales_invoice_id = create_sales_invoice_with_commission(doc, row)
    row.sales_invoice_commission = sales_invoice_id

    frappe.db.commit()

@frappe.whitelist()
def create_purchase_invoice(doc, row):
    """Create a purchase invoice."""
    try:
        commission = doc.commission or 0
        one_time_commission = doc.one_time_commission or 0
        net_amount = row.amount

        # Adjust amount based on conditions
        if doc.asset_owner == "Supplier" and one_time_commission > 0 and doc.start_date == row.schedule_date:
            commission_amount = ((commission + one_time_commission) / 100) * row.amount
        else:
            commission_amount = (commission / 100) * row.amount
        
        net_amount = row.amount - commission_amount

        # Create the purchase invoice
        purchase_invoice = frappe.get_doc({
            "doctype": "Purchase Invoice",
            "supplier": doc.supplier,
            "property": doc.asset,
            "property_name": doc.asset_name,
            "amount": net_amount,
            "tenancy_id": doc.name
        })
        purchase_invoice.insert()
        purchase_invoice.submit()

        frappe.msgprint("Purchase invoice created: {0}").format(purchase_invoice.name)
        return purchase_invoice.name
    except Exception as e:
        frappe.throw(f"Failed to create purchase invoice: {str(e)}")

@frappe.whitelist()
def create_purchase_payment_entry(doc, row):
    """Create a payment entry for the purchase invoice."""
    try:
        default_cash_account = frappe.get_value("Company", doc.company, "default_cash_account")
        if not default_cash_account:
            frappe.throw("No default cash account set for the company {0}.").format(doc.company)

        # Create the payment entry
        payment_entry = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Pay",
            "party_type": "Supplier",
            "party": doc.supplier,
            "paid_from": default_cash_account,
            "paid_amount": row.amount,
            "reference_no": row.reference_no,
            "posting_date": row.schedule_date
        })
        payment_entry.insert()
        payment_entry.submit()

        frappe.msgprint("Payment entry for purchase invoice created: {0}".format(payment_entry.name))
        return payment_entry.name
    except Exception as e:
        frappe.throw("Failed to create payment entry: {0}".format(str(e)))

@frappe.whitelist()
def create_sales_invoice_with_commission(doc, row):
    """Create a sales invoice with commission."""
    try:
        # Calculate commission
        commission = doc.commission or 0
        commission_amount = (commission / 100) * row.amount

        # Create the sales invoice
        sales_invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": doc.customer,
            "items": [{
                "item_name": "Commission",
                "rate": commission_amount,
                "amount": commission_amount
            }],
            "tenancy_id": doc.name
        })
        sales_invoice.insert()
        sales_invoice.submit()

        frappe.msgprint("Sales invoice created: {0}").format(sales_invoice.name)
        return sales_invoice.name
    except Exception as e:
        frappe.throw("Failed to create sales invoice: {0}".format(str(e)))

     
