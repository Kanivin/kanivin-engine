# Copyright (c) 2021, Kanivin and Contributors
# License: MIT. See LICENSE
import kanivin
from kanivin.installer import update_site_config
from kanivin.tests.utils import KanivinTestCase


class TestUserType(KanivinTestCase):
	def setUp(self):
		create_role()

	def test_add_select_perm_doctypes(self):
		user_type = create_user_type("Test User Type")

		# select perms added for all link fields
		doc = kanivin.get_meta("Contact")
		link_fields = doc.get_link_fields()
		select_doctypes = kanivin.get_all(
			"User Select Document Type", {"parent": user_type.name}, pluck="document_type"
		)

		for entry in link_fields:
			self.assertTrue(entry.options in select_doctypes)

		# select perms added for all child table link fields
		link_fields = []
		for child_table in doc.get_table_fields():
			child_doc = kanivin.get_meta(child_table.options)
			link_fields.extend(child_doc.get_link_fields())

		for entry in link_fields:
			self.assertTrue(entry.options in select_doctypes)

	def test_print_share_email_default(self):
		"""Test if print, share & email values default to 1. (for backward compatibility)"""
		# create user type with read, write permissions
		create_user_type("Test User Type")

		# check if print, share & email values are set to 1
		perm = kanivin.get_all("Custom DocPerm", filters={"role": "_Test User Type"}, fields=["*"])[0]

		self.assertTrue(perm.print == 1)
		self.assertTrue(perm.share == 1)
		self.assertTrue(perm.email == 1)

	def tearDown(self):
		kanivin.db.rollback()


def create_user_type(user_type):
	if kanivin.db.exists("User Type", user_type):
		kanivin.delete_doc("User Type", user_type)

	user_type_limit = {kanivin.scrub(user_type): 1}
	update_site_config("user_type_doctype_limit", user_type_limit)

	doc = kanivin.get_doc(
		{
			"doctype": "User Type",
			"name": user_type,
			"role": "_Test User Type",
			"user_id_field": "user",
			"apply_user_permission_on": "User",
		}
	)

	doc.append("user_doctypes", {"document_type": "Contact", "read": 1, "write": 1})

	return doc.insert()


def create_role():
	if not kanivin.db.exists("Role", "_Test User Type"):
		kanivin.get_doc(
			{"doctype": "Role", "role_name": "_Test User Type", "desk_access": 1, "is_custom": 1}
		).insert()
