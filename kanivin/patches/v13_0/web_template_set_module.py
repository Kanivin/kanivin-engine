# Copyright (c) 2020, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import kanivin


def execute():
	"""Set default module for standard Web Template, if none."""
	kanivin.reload_doc("website", "doctype", "Web Template Field")
	kanivin.reload_doc("website", "doctype", "web_template")

	standard_templates = kanivin.get_list("Web Template", {"standard": 1})
	for template in standard_templates:
		doc = kanivin.get_doc("Web Template", template.name)
		if not doc.module:
			doc.module = "Website"
			doc.save()
