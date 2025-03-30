# Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import kanivin


def add_custom_field(doctype, fieldname, fieldtype="Data", options=None):
	kanivin.get_doc(
		{
			"doctype": "Custom Field",
			"dt": doctype,
			"fieldname": fieldname,
			"fieldtype": fieldtype,
			"options": options,
		}
	).insert()


def clear_custom_fields(doctype):
	kanivin.db.delete("Custom Field", {"dt": doctype})
	kanivin.clear_cache(doctype=doctype)
