# Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import kanivin
from kanivin.core.doctype.role.role import get_info_based_on_role
from kanivin.tests.utils import KanivinTestCase

test_records = kanivin.get_test_records("Role")


class TestUser(KanivinTestCase):
	def test_disable_role(self):
		kanivin.get_doc("User", "test@example.com").add_roles("_Test Role 3")

		role = kanivin.get_doc("Role", "_Test Role 3")
		role.disabled = 1
		role.save()

		self.assertTrue("_Test Role 3" not in kanivin.get_roles("test@example.com"))

		role = kanivin.get_doc("Role", "_Test Role 3")
		role.disabled = 0
		role.save()

		kanivin.get_doc("User", "test@example.com").add_roles("_Test Role 3")
		self.assertTrue("_Test Role 3" in kanivin.get_roles("test@example.com"))

	def test_change_desk_access(self):
		"""if we change desk acecss from role, remove from user"""
		kanivin.delete_doc_if_exists("User", "test-user-for-desk-access@example.com")
		kanivin.delete_doc_if_exists("Role", "desk-access-test")
		user = kanivin.get_doc(
			dict(doctype="User", email="test-user-for-desk-access@example.com", first_name="test")
		).insert()
		role = kanivin.get_doc(dict(doctype="Role", role_name="desk-access-test", desk_access=0)).insert()
		user.add_roles(role.name)
		user.save()
		self.assertTrue(user.user_type == "Website User")
		role.desk_access = 1
		role.save()
		user.reload()
		self.assertTrue(user.user_type == "System User")
		role.desk_access = 0
		role.save()
		user.reload()
		self.assertTrue(user.user_type == "Website User")

	def test_get_users_by_role(self):
		role = "System Manager"
		sys_managers = get_info_based_on_role(role, field="name")

		for user in sys_managers:
			self.assertIn(role, kanivin.get_roles(user))
