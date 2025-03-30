# Copyright (c) 2020, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import kanivin


def execute():
	kanivin.reload_doc("Email", "doctype", "Notification")

	notifications = kanivin.get_all("Notification", {"is_standard": 1}, {"name", "channel"})
	for notification in notifications:
		if not notification.channel:
			kanivin.db.set_value("Notification", notification.name, "channel", "Email", update_modified=False)
			kanivin.db.commit()
