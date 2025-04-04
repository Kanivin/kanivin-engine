import frappe
from frappe.utils.install import add_standard_navbar_items


def execute():
	# Add standard navbar items for KANIERP in Navbar Settings
	frappe.reload_doc("core", "doctype", "navbar_settings")
	frappe.reload_doc("core", "doctype", "navbar_item")
	add_standard_navbar_items()
