# Copyright (c) 2020, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import kanivin


def execute():
	kanivin.reload_doc("core", "doctype", "DocField")

	if kanivin.db.has_column("DocField", "show_days"):
		kanivin.db.sql(
			"""
			UPDATE
				tabDocField
			SET
				hide_days = 1 WHERE show_days = 0
		"""
		)
		kanivin.db.sql_ddl("alter table tabDocField drop column show_days")

	if kanivin.db.has_column("DocField", "show_seconds"):
		kanivin.db.sql(
			"""
			UPDATE
				tabDocField
			SET
				hide_seconds = 1 WHERE show_seconds = 0
		"""
		)
		kanivin.db.sql_ddl("alter table tabDocField drop column show_seconds")

	kanivin.clear_cache(doctype="DocField")
