# Copyright (c) 2025, Ketan Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LandItem(Document):
	def before_save(self):
		self.create_item()
		
	def create_item(self):
		item= frappe.new_doc('Item')
		item.custom_company = 'ALI HAIDER PORTFOLIO'
		item.item_code = self.property_item_code
		item.item_name = self.property_item_name
		item.item_group = "Land for Sale"
		item.is_grouped_asset = 1
		item.is_fixed_asset = 1
		item.is_stock_item = 0
		item.asset_category = "Land for Sale"
		item.stock_uom = "Square Meter"
		
		item.insert(ignore_permissions=True)
		item.save()
	
