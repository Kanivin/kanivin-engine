import kanivin


def execute():
	doctype = "Top Bar Item"
	if not kanivin.db.table_exists(doctype) or not kanivin.db.has_column(doctype, "target"):
		return

	kanivin.reload_doc("website", "doctype", "top_bar_item")
	kanivin.db.set_value(doctype, {"target": 'target = "_blank"'}, "open_in_new_tab", 1)
