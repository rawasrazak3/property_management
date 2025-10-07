# Copyright (c) 2025, Ketan Patel and contributors
# For license information, please see license.txt


import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    columns = [
        {"label": "Shareholder", "fieldname": "shareholder", "fieldtype": "Data", "width": 200},
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 110},
        {"label": "Project Name", "fieldname": "project_name", "fieldtype": "Data", "width": 200},
        {"label": "Contribution %", "fieldname": "contribution", "fieldtype": "Percent", "width": 120},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 150},
        {"label": "Innitial Contribution %", "fieldname": "initial_contribution", "fieldtype": "Percent", "width": 120},
        {"label": "Initial_Amount", "fieldname": "initial_amount", "fieldtype": "Currency", "width": 150},
    ]

    data = []
    shareholder = filters.get("shareholder")

    if not shareholder:
        return columns, data
    
	# Fetch the full name of the selected shareholder
    shareholder_name = frappe.db.get_value("Shareholder", shareholder, "title")

    # Fetch all parent assets where split_from is empty
    properties = frappe.get_all(
        "Asset",
        filters={
            	"split_from": ["is", "not set"],
                 "docstatus": ["!=", 2]   # Exclude cancelled Assets
				},
        fields=["name", "asset_name","custom_project"]
    )

    for prop in properties:
        #fetch project name
        project_name = frappe.db.get_value("Project", prop.custom_project, "project_name")
        project_status = frappe.db.get_value("Project", prop.custom_project, "status")
        if project_status and project_status.lower() == "cancelled":
            continue
        # Fetch shareholder details from child table of each property
        shareholders = frappe.get_all(
            "Shareholder Property",  # replace with actual child table name
            filters={
                "parent": prop.name,
                "shareholder": shareholder
            },
            fields=["contribution", "amount","actual_contribution","actual_amount"]
        )
        for sh in shareholders:
            data.append({
                "shareholder": shareholder_name,
                "project": prop.custom_project,
                "project_name": project_name,
                "contribution": sh.contribution,
                "amount": sh.amount,
                "initial_contribution": sh.actual_contribution,
                "initial_amount": sh.actual_amount
            })

    return columns, data
