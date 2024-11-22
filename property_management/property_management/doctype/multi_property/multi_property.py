# Copyright (c) 2024, Ketan Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class MultiProperty(Document):
    def before_save(self):
        total_units = sum(
            (row.total_resident_unit or 0) + (row.total_commercial_unit or 0)
            for row in self.floor_details
        )
        
        if total_units != self.split_quantity:
            frappe.throw(_("The total of resident and commercial units must equal the split quantity."))

    def on_submit(self):
        self.create_items_and_assets()

    def create_items_and_assets(self):
        for row in self.multi_property_table:
            item_doc = frappe.get_doc({
                "doctype": "Item",
                "item_code": row.item_code,
                "item_name": row.item_name,
                "item_group": "Flat",
                "is_stock_item": 0,
                "is_fixed_asset": 1,
                "asset_category": "Residential and Commercial",
                "stock_uom": "Square Meter"
            })
            item_doc.insert(ignore_permissions=True)

            asset_doc = frappe.get_doc({
                "doctype": "Asset",
                "asset_name": f"{row.name_prefix} - {row.item_code}",
                "gfa_sqft": row.size,
                "gross_purchase_amount": row.gross_amount,
                "item_code": row.item_code,
                "location": self.property,
                "available_for_use_date": self.available_for_use,
                "purchase_date": self.purchase_date,
                "custom_property_type": "Land",
                "is_existing_asset": 1,
                "custom_against_property": self.property
            })
            asset_doc.insert(ignore_permissions=True)

    @frappe.whitelist()
    def split_property(self):
        self.multi_property_table = []
        prefix = self.name_prefix
        size_per_unit = self.qty / self.split_quantity
        row_number = 1

        for floor in self.floor_details:
            for unit_type, unit_count in [
                ("Resident", floor.total_resident_unit or 0),
                ("Commercial", floor.total_commercial_unit or 0),
            ]:
                for unit in range(1, unit_count + 1):
                    if row_number > self.split_quantity:
                        break

                    self.append(
                        "multi_property_table",
                        {
                            "name_prefix": f"{prefix}-{row_number:03d}",
                            "size": size_per_unit,
                            "gross_amount": self.unit_price,
                            "item_code": f"{self.item_code}-{floor.floor_no}-{unit_type[0]}{unit:02d}",
                            "item_name": self.item_name,
                            "floor_no": floor.floor_no,
                            "unit_type": unit_type,
                        },
                    )
                    row_number += 1
        self.save()
        frappe.msgprint(_("Property split successfully."))
