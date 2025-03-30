# Copyright (c) 2019, Kanivin and Contributors
# License: MIT. See LICENSE
import kanivin
from kanivin.core.doctype.user.user import get_system_users
from kanivin.desk.form.assign_to import add as assign_task
from kanivin.tests.utils import KanivinTestCase


class TestNotificationLog(KanivinTestCase):
	def test_assignment(self):
		todo = get_todo()
		user = get_user()

		assign_task(
			{"assign_to": [user], "doctype": "ToDo", "name": todo.name, "description": todo.description}
		)
		log_type = kanivin.db.get_value(
			"Notification Log", {"document_type": "ToDo", "document_name": todo.name}, "type"
		)
		self.assertEqual(log_type, "Assignment")

	def test_share(self):
		todo = get_todo()
		user = get_user()

		kanivin.share.add("ToDo", todo.name, user, notify=1)
		log_type = kanivin.db.get_value(
			"Notification Log", {"document_type": "ToDo", "document_name": todo.name}, "type"
		)
		self.assertEqual(log_type, "Share")

		email = get_last_email_queue()
		content = f"Subject: {kanivin.utils.get_fullname(kanivin.session.user)} shared a document ToDo"
		self.assertTrue(content in email.message)


def get_last_email_queue():
	res = kanivin.get_all("Email Queue", fields=["message"], order_by="creation desc", limit=1)
	return res[0]


def get_todo():
	if not kanivin.get_all("ToDo"):
		return kanivin.get_doc({"doctype": "ToDo", "description": "Test for Notification"}).insert()

	res = kanivin.get_all("ToDo", limit=1)
	return kanivin.get_cached_doc("ToDo", res[0].name)


def get_user():
	return get_system_users(limit=1)[0]
