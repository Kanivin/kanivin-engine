import kanivin


def execute():
	kanivin.reload_doc("core", "doctype", "doctype_link")
	kanivin.reload_doc("core", "doctype", "doctype_action")
	kanivin.reload_doc("core", "doctype", "doctype")
	kanivin.model.delete_fields({"DocType": ["hide_heading", "image_view", "read_only_onload"]}, delete=1)

	kanivin.db.delete("Property Setter", {"property": "read_only_onload"})
