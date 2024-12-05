from . import __version__ as app_version

app_name = "property_management"
app_title = "Property Management"
app_publisher = "Ketan Patel"
app_description = "Property Management system for Real Estate Vertical"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "contact@solufy.in"
app_license = "MIT"

# Includes in <head>
# ------------------
fixtures = [
	{
		"doctype": "Translation"
	},
	{
    "doctype": "Property Setter",
        "filters": {
            "module": ["in", ["Property Management"]]
            }
    },
    {
        "doctype":"Custom Field",
		"filters": [
            [
                "name",
                "in",
                [
                    "Asset-custom_advance_payment_details",
                    "Asset-custom_advance_amount",
                    "Asset-custom_journal_entry_id",
                    "Asset-custom_column_break_cwiwt",
                    "Asset-custom_tenant",
                    "Asset-custom_column_break_pr7vi",
                    "Asset-custom_mode_of_payment",
                    "Tenancy-custom_contract",
				]
			]
		]
	}
	]
# include js, css files in header of desk.html
# app_include_css = "/assets/property_management/css/property_management.css"
# app_include_js = "/assets/property_management/js/property_management.js"

# include js, css files in header of web template
# web_include_css = "/assets/property_management/css/property_management.css"
# web_include_js = "/assets/property_management/js/property_management.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "property_management/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_js = {
			"Asset" : "public/js/asset.js",
			"Contract" : "public/js/contract.js",
			"Customer" : "public/js/customer.js",
			"Event" : "public/js/event.js",
            "Journal Entry": "public/js/journal_entry.js"
			}
doctype_list_js = {
			"Asset" : "public/js/asset_list.js"
			}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "property_management.install.before_install"
# after_install = "property_management.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "property_management.uninstall.before_uninstall"
# after_uninstall = "property_management.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "property_management.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

doc_events = {
	"Tenancy": {
		"on_submit": "property_management.property_management.doctype.tenancy.tenancy.tenant_schedule",
        "before_save": "property_management.property_management.doctype.tenancy.tenancy.create_contract_on_tenancy_save"	
	},

	"Asset": {
		"on_submit": [
            "property_management.api.crud_event.rent_item",
        	"property_management.property_management.custom_script.asset.submit_asset_with_advance"
        ]
	},

	"Property Owner": {
		"on_change": "property_management.property_management.doctype.property_owner.property_owner.create_property_owner_customer"
	},

	"Property Manager": {
		"on_change": "property_management.property_management.doctype.property_manager.property_manager.create_property_manager_customer"
	},

	"Tenant": {
		"on_change": "property_management.property_management.doctype.tenant.tenant.create_tenant_customer"
	},

	"Landlord": {
		"on_change": "property_management.property_management.doctype.landlord.landlord.create_landlord_customer"
	},
    "Sales Invoice": {
		"on_submit": "property_management.property_management.custom_script.sales_invoice.create_payment_entry_from_sales_invoice"
	},
    "Journal Entry": {
		"on_submit": [
			"property_management.property_management.custom_script.journal_entry.update_shareholder_expenses",
			"property_management.property_management.custom_script.journal_entry.update_shareholder_exit"
		]
	},
    "Tenancy Termination":{
        "before_submit" : [
            "property_management.property_management.doctype.tenancy_termination.tenancy_termination.create_journal_entry",
            "property_management.property_management.doctype.tenancy_termination.tenancy_termination.manage_property_on_termination",
            "property_management.property_management.doctype.tenancy_termination.tenancy_termination.create_invoice_on_tenency_exit",
		]
	} 

}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"property_management.tasks.all"
# 	],
# 	"daily": [
# 		"property_management.tasks.daily"
# 	],
# 	"hourly": [
# 		"property_management.tasks.hourly"
# 	],
# 	"weekly": [
# 		"property_management.tasks.weekly"
# 	]
# 	"monthly": [
# 		"property_management.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "property_management.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "property_management.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "property_management.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"property_management.auth.validate"
# ]

# Translation
# --------------------------------

# Make link fields search translated document names for these DocTypes
# Recommended only for DocTypes which have limited documents with untranslated names
# For example: Role, Gender, etc.
# translated_search_doctypes = []

# fixtures = [
#     {
#         "doctype": "Property Setter",
#         "filters": [
#             ["doc_type", "=", "Sales Invoice"],
#         ]
#     }
# ]