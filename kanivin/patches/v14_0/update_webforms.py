# Copyright (c) 2021, Kanivin Pvt. Ltd. and Contributors
# MIT License. See license.txt


import kanivin


def execute():
	kanivin.reload_doc("website", "doctype", "web_form_list_column")
	kanivin.reload_doctype("Web Form")

	for web_form in kanivin.get_all("Web Form", fields=["*"]):
		if web_form.allow_multiple and not web_form.show_list:
			kanivin.db.set_value("Web Form", web_form.name, "show_list", True)
