# Copyright (c) 2024, Ketan Patel and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns, data = get_columns(filters), get_data(filters)
    return columns, data

def get_columns(filters):
    columns = [
        {
            "label": _("Company"),
            "fieldname": "company",
            "fieldtype": "Link",
            "options": "Company",
            "width": 95,
        },
        {
            "label": _("Customer"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 170,
        },
        {
            "label": _("Maintenance Request Date"),
            "fieldname": "mntc_date",
            "fieldtype": "Date",
            "width": 150,
        },
        {
            "fieldname": "maintenance_type",
            "label": "Maintenance Type",
            "fieldtype": "Select",
            "options": "Scheduled\nUnscheduled\nBreakdown",
            "width": 150,
        },
        {
            "label": _("Property Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Property Name"),
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Charge Amount"),
            "fieldname": "custom_charge_amount",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": _("Sales Person"),
            "fieldname": "service_person",
            "fieldtype": "Link",
            "options" :"Sales Person",
            "width": 150,
        },
        {
            "label": _("Payment Status"),
            "fieldname": "custom_payment_status",
            "fieldtype": "Data",
            "options": "Unpaid\nPartially Paid\nPaid",
            "width": 150,
        },
    ]
    return columns

def get_data(filters):
    query = """
        SELECT
            msc.company, msc.customer, msc.mntc_date, msc.maintenance_type,
            pit.item_code, pit.item_name, pit.custom_charge_amount, pit.service_person, pit.custom_payment_status
        FROM
            `tabMaintenance Service Charge` msc
        LEFT JOIN
            `tabMaintenance Visit Purpose` pit ON pit.parent = msc.name
        WHERE
            msc.docstatus = 1 {conditions}
    """.format(
        conditions=get_conditions(filters)
    )

    return frappe.db.sql(query, filters, as_dict=1)

def get_conditions(filters):
    conditions = []

    if filters.get("customer"):
        conditions.append(" and msc.customer = %(customer)s")

    # Add other conditions if needed (e.g., company, date, etc.)
    if filters.get("company"):
        conditions.append(" and msc.company = %(company)s")

    if filters.get("mntc_date"):
        conditions.append(" and msc.mntc_date = %(mntc_date)s")

    if filters.get("item_code"):
        conditions.append(" and pit.item_code = %(item_code)s")

    # Join the conditions into a single string
    return " ".join(conditions) if conditions else ""
