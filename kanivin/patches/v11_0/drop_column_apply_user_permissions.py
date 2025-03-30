import kanivin


def execute():
	column = "apply_user_permissions"
	to_remove = ["DocPerm", "Custom DocPerm"]

	for doctype in to_remove:
		if kanivin.db.table_exists(doctype):
			if column in kanivin.db.get_table_columns(doctype):
				kanivin.db.sql(f"alter table `tab{doctype}` drop column {column}")

	kanivin.reload_doc("core", "doctype", "docperm", force=True)
	kanivin.reload_doc("core", "doctype", "custom_docperm", force=True)
