import kanivin
from kanivin.model.rename_doc import rename_doc


def execute():
	if kanivin.db.table_exists("Standard Reply") and not kanivin.db.table_exists("Email Template"):
		rename_doc("DocType", "Standard Reply", "Email Template")
		kanivin.reload_doc("email", "doctype", "email_template")
