# Copyright (c) 2019, Kanivin and Contributors
# License: MIT. See LICENSE
import json

import kanivin
from kanivin.contacts.doctype.contact.contact import get_contact_name
from kanivin.core.doctype.user.user import create_contact
from kanivin.tests.utils import KanivinTestCase
from kanivin.website.doctype.personal_data_download_request.personal_data_download_request import (
	get_user_data,
)


class TestRequestPersonalData(KanivinTestCase):
	def setUp(self):
		create_user_if_not_exists(email="test_privacy@example.com")

	def tearDown(self):
		kanivin.db.delete("Personal Data Download Request")

	def test_user_data_creation(self):
		user_data = json.loads(get_user_data("test_privacy@example.com"))
		contact_name = get_contact_name("test_privacy@example.com")
		expected_data = {"Contact": kanivin.get_all("Contact", {"name": contact_name}, ["*"])}
		expected_data = json.loads(json.dumps(expected_data, default=str))
		self.assertEqual({"Contact": user_data["Contact"]}, expected_data)

	def test_file_and_email_creation(self):
		kanivin.set_user("test_privacy@example.com")
		download_request = kanivin.get_doc(
			{"doctype": "Personal Data Download Request", "user": "test_privacy@example.com"}
		)
		download_request.save(ignore_permissions=True)

		kanivin.set_user("Administrator")

		file_count = kanivin.db.count(
			"File",
			{
				"attached_to_doctype": "Personal Data Download Request",
				"attached_to_name": download_request.name,
			},
		)

		self.assertEqual(file_count, 1)

		email_queue = kanivin.get_all("Email Queue", fields=["message"], order_by="creation DESC", limit=1)
		self.assertIn(kanivin._("Download Your Data"), email_queue[0].message)

		kanivin.db.delete("Email Queue")


def create_user_if_not_exists(email, first_name=None):
	kanivin.delete_doc_if_exists("User", email)

	user = kanivin.get_doc(
		{
			"doctype": "User",
			"user_type": "Website User",
			"email": email,
			"send_welcome_email": 0,
			"first_name": first_name or email.split("@", 1)[0],
			"birth_date": kanivin.utils.now_datetime(),
		}
	).insert(ignore_permissions=True)
	create_contact(user=user)
