import kanivin
from kanivin.model.rename_doc import rename_doc


def execute():
	if kanivin.db.table_exists("Email Alert Recipient") and not kanivin.db.table_exists(
		"Notification Recipient"
	):
		rename_doc("DocType", "Email Alert Recipient", "Notification Recipient")
		kanivin.reload_doc("email", "doctype", "notification_recipient")

	if kanivin.db.table_exists("Email Alert") and not kanivin.db.table_exists("Notification"):
		rename_doc("DocType", "Email Alert", "Notification")
		kanivin.reload_doc("email", "doctype", "notification")
