# Copyright (c) 2015, Kanivin Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import frappe
from frappe.cache_manager import clear_controller_cache
from frappe.desk.doctype.todo.todo import ToDo
from frappe.tests.test_api import KanivinAPITestCase
from frappe.tests.utils import KanivinTestCase, patch_hooks


class TestHooks(KanivinTestCase):
	def test_hooks(self):
		hooks = frappe.get_hooks()
		self.assertTrue(isinstance(hooks.get("app_name"), list))
		self.assertTrue(isinstance(hooks.get("doc_events"), dict))
		self.assertTrue(isinstance(hooks.get("doc_events").get("*"), dict))
		self.assertTrue(isinstance(hooks.get("doc_events").get("*"), dict))
		self.assertTrue(
			"frappe.desk.notifications.clear_doctype_notifications"
			in hooks.get("doc_events").get("*").get("on_update")
		)

	def test_override_doctype_class(self):
		from frappe import hooks

		# Set hook
		hooks.override_doctype_class = {"ToDo": ["frappe.tests.test_hooks.CustomToDo"]}

		# Clear cache
		frappe.cache.delete_value("app_hooks")
		clear_controller_cache("ToDo")

		todo = frappe.get_doc(doctype="ToDo", description="asdf")
		self.assertTrue(isinstance(todo, CustomToDo))

	def test_has_permission(self):
		from frappe import hooks

		# Set hook
		address_has_permission_hook = hooks.has_permission.get("Address", [])
		if isinstance(address_has_permission_hook, str):
			address_has_permission_hook = [address_has_permission_hook]

		address_has_permission_hook.append("frappe.tests.test_hooks.custom_has_permission")

		hooks.has_permission["Address"] = address_has_permission_hook

		wildcard_has_permission_hook = hooks.has_permission.get("*", [])
		if isinstance(wildcard_has_permission_hook, str):
			wildcard_has_permission_hook = [wildcard_has_permission_hook]

		wildcard_has_permission_hook.append("frappe.tests.test_hooks.custom_has_permission")

		hooks.has_permission["*"] = wildcard_has_permission_hook

		# Clear cache
		frappe.cache.delete_value("app_hooks")

		# Init User and Address
		username = "test@example.com"
		user = frappe.get_doc("User", username)
		user.add_roles("System Manager")
		address = frappe.new_doc("Address")

		# Create Note
		note = frappe.new_doc("Note")
		note.public = 1

		# Test!
		self.assertTrue(frappe.has_permission("Address", doc=address, user=username))
		self.assertTrue(frappe.has_permission("Note", doc=note, user=username))

		address.flags.dont_touch_me = True
		self.assertFalse(frappe.has_permission("Address", doc=address, user=username))

		note.flags.dont_touch_me = True
		self.assertFalse(frappe.has_permission("Note", doc=note, user=username))

	def test_ignore_links_on_delete(self):
		email_unsubscribe = frappe.get_doc(
			{"doctype": "Email Unsubscribe", "email": "test@example.com", "global_unsubscribe": 1}
		).insert()

		event = frappe.get_doc(
			{
				"doctype": "Event",
				"subject": "Test Event",
				"starts_on": "2022-12-21",
				"event_type": "Public",
				"event_participants": [
					{
						"reference_doctype": "Email Unsubscribe",
						"reference_docname": email_unsubscribe.name,
					}
				],
			}
		).insert()
		self.assertRaises(frappe.LinkExistsError, email_unsubscribe.delete)

		event.event_participants = []
		event.save()

		todo = frappe.get_doc(
			{
				"doctype": "ToDo",
				"description": "Test ToDo",
				"reference_type": "Event",
				"reference_name": event.name,
			}
		)
		todo.insert()

		event.delete()


class TestAPIHooks(KanivinAPITestCase):
	def test_auth_hook(self):
		with patch_hooks({"auth_hooks": ["frappe.tests.test_hooks.custom_auth"]}):
			site_url = frappe.utils.get_site_url(frappe.local.site)
			response = self.get(
				site_url + "/api/method/frappe.auth.get_logged_user",
				headers={"Authorization": "Bearer set_test_example_user"},
			)
			# Test!
			self.assertTrue(response.json.get("message") == "test@example.com")


def custom_has_permission(doc, ptype, user):
	if doc.flags.dont_touch_me:
		return False


def custom_auth():
	auth_type, token = frappe.get_request_header("Authorization", "Bearer ").split(" ")
	if token == "set_test_example_user":
		frappe.set_user("test@example.com")


class CustomToDo(ToDo):
	pass
