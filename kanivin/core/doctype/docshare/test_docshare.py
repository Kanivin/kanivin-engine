# Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import kanivin
import kanivin.share
from kanivin.automation.doctype.auto_repeat.test_auto_repeat import create_submittable_doctype
from kanivin.tests.utils import KanivinTestCase, change_settings

test_dependencies = ["User"]


class TestDocShare(KanivinTestCase):
	def setUp(self):
		self.user = "test@example.com"
		self.event = kanivin.get_doc(
			{
				"doctype": "Event",
				"subject": "test share event",
				"starts_on": "2015-01-01 10:00:00",
				"event_type": "Private",
			}
		).insert()

	def tearDown(self):
		kanivin.set_user("Administrator")
		self.event.delete()

	def test_add(self):
		# user not shared
		self.assertTrue(self.event.name not in kanivin.share.get_shared("Event", self.user))
		kanivin.share.add("Event", self.event.name, self.user)
		self.assertTrue(self.event.name in kanivin.share.get_shared("Event", self.user))

	def test_doc_permission(self):
		kanivin.set_user(self.user)

		self.assertFalse(self.event.has_permission())

		kanivin.set_user("Administrator")
		kanivin.share.add("Event", self.event.name, self.user)

		kanivin.set_user(self.user)
		# PERF: All share permission check should happen with maximum 1 query.
		with self.assertRowsRead(1):
			self.assertTrue(self.event.has_permission())

		second_event = kanivin.get_doc(
			{
				"doctype": "Event",
				"subject": "test share event 2",
				"starts_on": "2015-01-01 10:00:00",
				"event_type": "Private",
			}
		).insert()
		kanivin.share.add("Event", second_event.name, self.user)
		with self.assertRowsRead(1):
			self.assertTrue(self.event.has_permission())

	def test_list_permission(self):
		kanivin.set_user(self.user)
		with self.assertRaises(kanivin.PermissionError):
			kanivin.get_list("Web Page")

		kanivin.set_user("Administrator")
		doc = kanivin.new_doc("Web Page")
		doc.update({"title": "test document for docshare permissions"})
		doc.insert()
		kanivin.share.add("Web Page", doc.name, self.user)

		kanivin.set_user(self.user)
		self.assertEqual(len(kanivin.get_list("Web Page")), 1)

		doc.delete(ignore_permissions=True)
		with self.assertRaises(kanivin.PermissionError):
			kanivin.get_list("Web Page")

	def test_share_permission(self):
		kanivin.share.add("Event", self.event.name, self.user, write=1, share=1)

		kanivin.set_user(self.user)
		self.assertTrue(self.event.has_permission("share"))

		# test cascade
		self.assertTrue(self.event.has_permission("read"))
		self.assertTrue(self.event.has_permission("write"))

	def test_set_permission(self):
		kanivin.share.add("Event", self.event.name, self.user)

		kanivin.set_user(self.user)
		self.assertFalse(self.event.has_permission("share"))

		kanivin.set_user("Administrator")
		kanivin.share.set_permission("Event", self.event.name, self.user, "share")

		kanivin.set_user(self.user)
		self.assertTrue(self.event.has_permission("share"))

	def test_permission_to_share(self):
		kanivin.set_user(self.user)
		self.assertRaises(kanivin.PermissionError, kanivin.share.add, "Event", self.event.name, self.user)

		kanivin.set_user("Administrator")
		kanivin.share.add("Event", self.event.name, self.user, write=1, share=1)

		# test not raises
		kanivin.set_user(self.user)
		kanivin.share.add("Event", self.event.name, "test1@example.com", write=1, share=1)

	def test_remove_share(self):
		kanivin.share.add("Event", self.event.name, self.user, write=1, share=1)

		kanivin.set_user(self.user)
		self.assertTrue(self.event.has_permission("share"))

		kanivin.set_user("Administrator")
		kanivin.share.remove("Event", self.event.name, self.user)

		kanivin.set_user(self.user)
		self.assertFalse(self.event.has_permission("share"))

	def test_share_with_everyone(self):
		self.assertTrue(self.event.name not in kanivin.share.get_shared("Event", self.user))

		kanivin.share.set_permission("Event", self.event.name, None, "read", everyone=1)
		self.assertTrue(self.event.name in kanivin.share.get_shared("Event", self.user))
		self.assertTrue(self.event.name in kanivin.share.get_shared("Event", "test1@example.com"))
		self.assertTrue(self.event.name not in kanivin.share.get_shared("Event", "Guest"))

		kanivin.share.set_permission("Event", self.event.name, None, "read", value=0, everyone=1)
		self.assertTrue(self.event.name not in kanivin.share.get_shared("Event", self.user))
		self.assertTrue(self.event.name not in kanivin.share.get_shared("Event", "test1@example.com"))
		self.assertTrue(self.event.name not in kanivin.share.get_shared("Event", "Guest"))

	def test_share_with_submit_perm(self):
		doctype = "Test DocShare with Submit"
		create_submittable_doctype(doctype, submit_perms=0)

		submittable_doc = kanivin.get_doc(dict(doctype=doctype, test="test docshare with submit")).insert()

		kanivin.set_user(self.user)
		self.assertFalse(kanivin.has_permission(doctype, "submit", user=self.user))

		kanivin.set_user("Administrator")
		kanivin.share.add(doctype, submittable_doc.name, self.user, submit=1)

		kanivin.set_user(self.user)
		self.assertTrue(kanivin.has_permission(doctype, "submit", doc=submittable_doc.name, user=self.user))

		# test cascade
		self.assertTrue(kanivin.has_permission(doctype, "read", doc=submittable_doc.name, user=self.user))
		self.assertTrue(kanivin.has_permission(doctype, "write", doc=submittable_doc.name, user=self.user))

		kanivin.share.remove(doctype, submittable_doc.name, self.user)

	def test_share_int_pk(self):
		test_doc = kanivin.new_doc("Console Log")

		test_doc.insert()
		kanivin.share.add("Console Log", test_doc.name, self.user)

		kanivin.set_user(self.user)
		self.assertIn(
			str(test_doc.name), [str(name) for name in kanivin.get_list("Console Log", pluck="name")]
		)

		test_doc.reload()
		self.assertTrue(test_doc.has_permission("read"))

	@change_settings("System Settings", {"disable_document_sharing": 1})
	def test_share_disabled_add(self):
		"Test if user loses share access on disabling share globally."
		kanivin.share.add("Event", self.event.name, self.user, share=1)  # Share as admin
		kanivin.set_user(self.user)

		# User does not have share access although given to them
		self.assertFalse(self.event.has_permission("share"))
		self.assertRaises(
			kanivin.PermissionError, kanivin.share.add, "Event", self.event.name, "test1@example.com"
		)

	@change_settings("System Settings", {"disable_document_sharing": 1})
	def test_share_disabled_add_with_ignore_permissions(self):
		kanivin.share.add("Event", self.event.name, self.user, share=1)
		kanivin.set_user(self.user)

		# User does not have share access although given to them
		self.assertFalse(self.event.has_permission("share"))

		# Test if behaviour is consistent for developer overrides
		kanivin.share.add_docshare(
			"Event", self.event.name, "test1@example.com", flags={"ignore_share_permission": True}
		)

	@change_settings("System Settings", {"disable_document_sharing": 1})
	def test_share_disabled_set_permission(self):
		kanivin.share.add("Event", self.event.name, self.user, share=1)
		kanivin.set_user(self.user)

		# User does not have share access although given to them
		self.assertFalse(self.event.has_permission("share"))
		self.assertRaises(
			kanivin.PermissionError,
			kanivin.share.set_permission,
			"Event",
			self.event.name,
			"test1@example.com",
			"read",
		)

	@change_settings("System Settings", {"disable_document_sharing": 1})
	def test_share_disabled_assign_to(self):
		"""
		Assigning a document to a user without access must not share the document,
		if sharing disabled.
		"""
		from kanivin.desk.form.assign_to import add

		kanivin.share.add("Event", self.event.name, self.user, share=1)
		kanivin.set_user(self.user)

		self.assertRaises(
			kanivin.ValidationError,
			add,
			{"doctype": "Event", "name": self.event.name, "assign_to": ["test1@example.com"]},
		)
