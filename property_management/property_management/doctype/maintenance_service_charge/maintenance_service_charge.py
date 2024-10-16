# Copyright (c) 2024, Ketan Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MaintenanceServiceCharge(Document):
    pass

# @frappe.whitelist()
# def create_maintenance_service_charge(customer, property):
#     # Create a new Maintenance Service Charge document
#     doc = frappe.get_doc({
#         "doctype": "Maintenance Service Charge",
#         "customer": customer,
#         "property": property,  # Set fields as needed
#         "mntc_date": frappe.utils.nowdate(),
#     })
    
#     doc.insert(ignore_permissions=True)
    
#     # Return the name of the newly created document
#     return doc.name
