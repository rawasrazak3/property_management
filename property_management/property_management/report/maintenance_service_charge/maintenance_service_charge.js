// Copyright (c) 2024, Ketan Patel and contributors
// For license information, please see license.txt

frappe.query_reports["Maintenance Service Charge"] = {
	"filters": [

		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("company"),
			"reqd": 1
		},
		{
			"fieldname": "mntc_date",
			"label": __("Maintenance Request Date"),
			"fieldtype": "Date",
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
		},
		{
            "fieldname": "item_code",
            "label": __("Property Item Code"),
            "fieldtype": "Link",
            "options": "Item",  // Make sure this points to the correct "Item" doctype
        }
	],
};
