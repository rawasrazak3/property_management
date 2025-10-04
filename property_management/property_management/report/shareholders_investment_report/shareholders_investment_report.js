// Copyright (c) 2025, Ketan Patel and contributors
// For license information, please see license.txt


frappe.query_reports["Shareholders Investment Report"] = {
    "filters": [
        {
            "fieldname": "shareholder",
            "label": __("Shareholder"),
            "fieldtype": "Link",
            "options": "Shareholder",  // or Customer if you’re using Customer as shareholder
            "reqd": 1
        }
    ]
};
