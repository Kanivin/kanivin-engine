import kanivin
from kanivin.utils.install import add_standard_navbar_items


def execute():
	# Add standard navbar items for ERPNext in Navbar Settings
	kanivin.reload_doc("core", "doctype", "navbar_settings")
	kanivin.reload_doc("core", "doctype", "navbar_item")
	add_standard_navbar_items()
