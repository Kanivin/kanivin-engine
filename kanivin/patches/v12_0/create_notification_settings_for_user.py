import kanivin
from kanivin.desk.doctype.notification_settings.notification_settings import (
	create_notification_settings,
)


def execute():
	kanivin.reload_doc("desk", "doctype", "notification_settings")
	kanivin.reload_doc("desk", "doctype", "notification_subscribed_document")

	users = kanivin.get_all("User", fields=["name"])
	for user in users:
		create_notification_settings(user.name)
