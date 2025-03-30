# Copyright (c) 2020, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import kanivin


def execute():
	kanivin.reload_doc("website", "doctype", "web_page_block")
	# remove unused templates
	kanivin.delete_doc("Web Template", "Navbar with Links on Right", force=1)
	kanivin.delete_doc("Web Template", "Footer Horizontal", force=1)
