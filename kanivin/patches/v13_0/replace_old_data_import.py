# Copyright (c) 2020, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import kanivin


def execute():
	if not kanivin.db.table_exists("Data Import"):
		return

	meta = kanivin.get_meta("Data Import")
	# if Data Import is the new one, return early
	if meta.fields[1].fieldname == "import_type":
		return

	kanivin.db.sql("DROP TABLE IF EXISTS `tabData Import Legacy`")
	kanivin.rename_doc("DocType", "Data Import", "Data Import Legacy")
	kanivin.db.commit()
	kanivin.db.sql("DROP TABLE IF EXISTS `tabData Import`")
	kanivin.rename_doc("DocType", "Data Import Beta", "Data Import")
