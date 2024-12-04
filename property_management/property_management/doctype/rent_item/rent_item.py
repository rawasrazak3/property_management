# Copyright (c) 2024, Ketan Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RentItem(Document):
	def before_save(self):
		self.create_item()
		
	def create_item(self):
		item= frappe.new_doc('Item')
		item.item_code = self.item_code
		item.item_name = self.item_name
		item.item_group = self.item_group
		item.is_stock_item = 0
		item.is_fixed_asset = 1
		item.asset_category = self.property_category
		item.stock_uom = self.unit_of_measure
		
		item.insert(ignore_permissions=True)
		item.save()




