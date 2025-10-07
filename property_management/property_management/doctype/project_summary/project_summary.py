# Copyright (c) 2025, Ketan Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProjectSummary(Document):
	pass

	def validate(self):
		self.calculate_totals()
		self.update_paid_profit()

	def calculate_totals(self):
		# ---- 1. Calculate Total Profit from Property Splits ----
		total_profit = 0
		for row in self.property_splits:
			total_profit += row.profit or 0

		self.total_profit = total_profit   # store in a parent field (make sure you have one)

		# ---- 2. Distribute Profit to Shareholders based on contribution % ----
		for sh in self.shareholder_details:
			contribution_percent = sh.contribution or 0
			sh.profit = (total_profit * contribution_percent) / 100 if contribution_percent else 0

	def update_paid_profit(self):
        # ---- 3. Update Paid Profit for each shareholder ----
		for sh in self.shareholder_details:
			if not sh.shareholder:
				continue

			# Get the linked party (assuming Shareholder is a Customer/Party)
			party = sh.shareholder
			print("party----",party)
			# Fetch sum of debits from Journal Entries
			paid_profit = frappe.db.sql("""
				SELECT SUM(jea.debit)
				FROM `tabJournal Entry` je
				INNER JOIN `tabJournal Entry Account` jea ON je.name = jea.parent
				WHERE je.docstatus = 1
				AND je.user_remark LIKE 'Profit Payout for Asset%%'
				AND jea.project = %s
				AND jea.party = %s
			""", (self.project, sh.shareholder), as_list=1)[0][0] or 0
			print("-----paid profit",paid_profit)
			sh.profit_paid = paid_profit

@frappe.whitelist()
def get_project_details(project_name):
	
		data = {
			"main_property": {},
			"properties": [],
			"shareholders": [],
			"expense":[]
		}

		# ---- Fetch Main Property of this project (not split) ----
		main_property = frappe.get_all(
			"Asset",
			filters={
				"custom_project": project_name,
				"split_from": ["is", "not set"],
				"docstatus": ["!=", 2]   # Exclude cancelled Assets
			},
			fields=["name", "asset_name", "status", "total_asset_cost"]
		)
		if main_property:
			main = main_property[0]
			data["main_property"] = {
				"name": main.name,
				"asset_name": main.asset_name,
				"status": main.status,
				"total_asset_cost": main.total_asset_cost
			}

			# ---- Fetch Shareholders from child table ----
			shareholders = frappe.get_all(
				"Shareholder Property",   # replace with your actual child table name
				filters={"parent": main.name},
				fields=["shareholder", "contribution", "amount","actual_contribution","actual_amount"]
			)
			for sh in shareholders:
				shareholder_name = frappe.db.get_value("Shareholder", sh.shareholder, "title")
				data["shareholders"].append({
					"shareholder": sh.shareholder,
					"shareholder_name": shareholder_name,
					"contribution": sh.contribution,
					"amount": sh.amount,
					"initial_contribution": sh.actual_contribution,
					"initial_amount": sh.actual_amount
				})
		#fetch total expense		
		total_expenses = frappe.db.sql("""
			SELECT SUM(total_expense_amount)
			FROM `tabExpense Property`
			WHERE custom_project = %s AND docstatus != 2
		""", (project_name,), as_list=1)[0][0] or 0

		data["total_expenses"] = total_expenses

		# ---- Fetch all Properties under this project ----
		properties = frappe.get_all(
			"Asset",
			filters={
				"custom_project": project_name,
				"docstatus": ["!=", 2]   # Exclude cancelled
			},
			fields=["name", "asset_name", "status", "custom_profit","gross_purchase_amount","custom_sales_invoice_id"]
		)
		for p in properties:
			selling_amount = 0

			if p.status == "Sold":
				selling_amount = frappe.db.sql("""
					SELECT SUM(si_item.amount)
					FROM `tabSales Invoice Item` si_item
					JOIN `tabSales Invoice` si ON si.name = si_item.parent
					WHERE si_item.asset = %s
					AND si.docstatus = 1
				""", (p.name,), as_list=1)[0][0] or 0

			data["properties"].append({
				"property": p.name,
				"property_name":p.asset_name,
				"status": p.status,
				"buying_price": p.gross_purchase_amount,
				"selling_price": selling_amount,
				"profit": p.custom_profit
			})

		

		return data

	
