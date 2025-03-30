# Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import json
import time
from contextlib import contextmanager
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from werkzeug.http import parse_cookie

import kanivin
import kanivin.exceptions
from kanivin.core.doctype.user.user import (
	User,
	handle_password_test_fail,
	reset_password,
	sign_up,
	test_password_strength,
	update_password,
	verify_password,
)
from kanivin.desk.notifications import extract_mentions
from kanivin.kanivinclient import KanivinClient
from kanivin.model.delete_doc import delete_doc
from kanivin.tests.test_api import KanivinAPITestCase
from kanivin.tests.utils import KanivinTestCase, change_settings
from kanivin.utils import get_url

user_module = kanivin.core.doctype.user.user
test_records = kanivin.get_test_records("User")


class TestUser(KanivinTestCase):
	def tearDown(self):
		# disable password strength test
		kanivin.db.set_single_value("System Settings", "enable_password_policy", 0)
		kanivin.db.set_single_value("System Settings", "minimum_password_score", "")
		kanivin.db.set_single_value("System Settings", "password_reset_limit", 3)
		kanivin.set_user("Administrator")

	@staticmethod
	def reset_password(user) -> str:
		link = user.reset_password()
		return parse_qs(urlparse(link).query)["key"][0]

	def test_user_type(self):
		user_id = kanivin.generate_hash() + "@example.com"
		new_user = kanivin.get_doc(doctype="User", email=user_id, first_name="Tester").insert()
		self.assertEqual(new_user.user_type, "Website User")

		# social login userid for kanivin
		self.assertTrue(new_user.social_logins[0].userid)
		self.assertEqual(new_user.social_logins[0].provider, "kanivin")

		# role with desk access
		new_user.add_roles("_Test Role 2")
		new_user.save()
		self.assertEqual(new_user.user_type, "System User")

		# clear role
		new_user.roles = []
		new_user.save()
		self.assertEqual(new_user.user_type, "Website User")

		# role without desk access
		new_user.add_roles("_Test Role 4")
		new_user.save()
		self.assertEqual(new_user.user_type, "Website User")

		delete_contact(new_user.name)
		kanivin.delete_doc("User", new_user.name)

	def test_delete(self):
		kanivin.get_doc("User", "test@example.com").add_roles("_Test Role 2")
		self.assertRaises(kanivin.LinkExistsError, delete_doc, "Role", "_Test Role 2")
		kanivin.db.delete("Has Role", {"role": "_Test Role 2"})
		delete_doc("Role", "_Test Role 2")

		if kanivin.db.exists("User", "_test@example.com"):
			delete_contact("_test@example.com")
			delete_doc("User", "_test@example.com")

		user = kanivin.copy_doc(test_records[1])
		user.email = "_test@example.com"
		user.insert()

		kanivin.get_doc({"doctype": "ToDo", "description": "_Test"}).insert()

		delete_contact("_test@example.com")
		delete_doc("User", "_test@example.com")

		self.assertTrue(
			not kanivin.db.sql("""select * from `tabToDo` where allocated_to=%s""", ("_test@example.com",))
		)

		from kanivin.core.doctype.role.test_role import test_records as role_records

		kanivin.copy_doc(role_records[1]).insert()

	def test_get_value(self):
		self.assertEqual(kanivin.db.get_value("User", "test@example.com"), "test@example.com")
		self.assertEqual(kanivin.db.get_value("User", {"email": "test@example.com"}), "test@example.com")
		self.assertEqual(
			kanivin.db.get_value("User", {"email": "test@example.com"}, "email"), "test@example.com"
		)
		self.assertEqual(
			kanivin.db.get_value("User", {"email": "test@example.com"}, ["first_name", "email"]),
			("_Test", "test@example.com"),
		)
		self.assertEqual(
			kanivin.db.get_value(
				"User", {"email": "test@example.com", "first_name": "_Test"}, ["first_name", "email"]
			),
			("_Test", "test@example.com"),
		)

		test_user = kanivin.db.sql("select * from tabUser where name='test@example.com'", as_dict=True)[0]
		self.assertEqual(
			kanivin.db.get_value("User", {"email": "test@example.com"}, "*", as_dict=True), test_user
		)

		self.assertEqual(kanivin.db.get_value("User", "xxxtest@example.com"), None)

		kanivin.db.set_single_value("Website Settings", "_test", "_test_val")
		self.assertEqual(kanivin.db.get_value("Website Settings", None, "_test"), "_test_val")
		self.assertEqual(kanivin.db.get_value("Website Settings", "Website Settings", "_test"), "_test_val")

	def test_high_permlevel_validations(self):
		user = kanivin.get_meta("User")
		self.assertTrue("roles" in [d.fieldname for d in user.get_high_permlevel_fields()])

		me = kanivin.get_doc("User", "testperm@example.com")
		me.remove_roles("System Manager")

		kanivin.set_user("testperm@example.com")

		me = kanivin.get_doc("User", "testperm@example.com")
		me.add_roles("System Manager")

		# system manager is not added (it is reset)
		self.assertFalse("System Manager" in [d.role for d in me.roles])

		# ignore permlevel using flags
		me.flags.ignore_permlevel_for_fields = ["roles"]
		me.add_roles("System Manager")

		# system manager now added due to flags
		self.assertTrue("System Manager" in [d.role for d in me.get("roles")])

		# reset flags
		me.flags.ignore_permlevel_for_fields = None

		# change user
		kanivin.set_user("Administrator")

		me = kanivin.get_doc("User", "testperm@example.com")
		me.add_roles("System Manager")

		# system manager now added by Administrator
		self.assertTrue("System Manager" in [d.role for d in me.get("roles")])

	def test_delete_user(self):
		new_user = kanivin.get_doc(
			dict(doctype="User", email="test-for-delete@example.com", first_name="Tester Delete User")
		).insert(ignore_if_duplicate=True)
		self.assertEqual(new_user.user_type, "Website User")

		# role with desk access
		new_user.add_roles("_Test Role 2")
		new_user.save()
		self.assertEqual(new_user.user_type, "System User")

		comm = kanivin.get_doc(
			{
				"doctype": "Communication",
				"subject": "To check user able to delete even if linked with communication",
				"content": "To check user able to delete even if linked with communication",
				"sent_or_received": "Sent",
				"user": new_user.name,
			}
		)
		comm.insert(ignore_permissions=True)

		delete_contact(new_user.name)
		kanivin.delete_doc("User", new_user.name)
		self.assertFalse(kanivin.db.exists("User", new_user.name))

	def test_password_strength(self):
		# Test Password without Password Strength Policy
		kanivin.db.set_single_value("System Settings", "enable_password_policy", 0)

		# password policy is disabled, test_password_strength should be ignored
		result = test_password_strength("test_password")
		self.assertFalse(result.get("feedback", None))

		# Test Password with Password Strenth Policy Set
		kanivin.db.set_single_value("System Settings", "enable_password_policy", 1)
		kanivin.db.set_single_value("System Settings", "minimum_password_score", 2)

		# Score 1; should now fail
		result = test_password_strength("bee2ve")
		self.assertEqual(result["feedback"]["password_policy_validation_passed"], False)
		self.assertRaises(kanivin.exceptions.ValidationError, handle_password_test_fail, result["feedback"])
		self.assertRaises(
			kanivin.exceptions.ValidationError, handle_password_test_fail, result
		)  # test backwards compatibility

		# Score 4; should pass
		result = test_password_strength("Eastern_43A1W")
		self.assertEqual(result["feedback"]["password_policy_validation_passed"], True)

		# test password strength while saving user with new password
		user = kanivin.get_doc("User", "test@example.com")
		kanivin.flags.in_test = False
		user.new_password = "password"
		self.assertRaises(kanivin.exceptions.ValidationError, user.save)
		user.reload()
		user.new_password = "Eastern_43A1W"
		user.save()
		kanivin.flags.in_test = True

	def test_comment_mentions(self):
		comment = """
			<span class="mention" data-id="test.comment@example.com" data-value="Test" data-denotation-char="@">
				<span><span class="ql-mention-denotation-char">@</span>Test</span>
			</span>
		"""
		self.assertEqual(extract_mentions(comment)[0], "test.comment@example.com")

		comment = """
			<div>
				Testing comment,
				<span class="mention" data-id="test.comment@example.com" data-value="Test" data-denotation-char="@">
					<span><span class="ql-mention-denotation-char">@</span>Test</span>
				</span>
				please check
			</div>
		"""
		self.assertEqual(extract_mentions(comment)[0], "test.comment@example.com")
		comment = """
			<div>
				Testing comment for
				<span class="mention" data-id="test_user@example.com" data-value="Test" data-denotation-char="@">
					<span><span class="ql-mention-denotation-char">@</span>Test</span>
				</span>
				and
				<span class="mention" data-id="test.again@example1.com" data-value="Test" data-denotation-char="@">
					<span><span class="ql-mention-denotation-char">@</span>Test</span>
				</span>
				please check
			</div>
		"""
		self.assertEqual(extract_mentions(comment)[0], "test_user@example.com")
		self.assertEqual(extract_mentions(comment)[1], "test.again@example1.com")

		kanivin.delete_doc("User Group", "Team")
		doc = kanivin.get_doc(
			{
				"doctype": "User Group",
				"name": "Team",
				"user_group_members": [{"user": "test@example.com"}, {"user": "test1@example.com"}],
			}
		)

		doc.insert()

		comment = """
			<div>
				Testing comment for
				<span class="mention" data-id="Team" data-value="Team" data-is-group="true" data-denotation-char="@">
					<span><span class="ql-mention-denotation-char">@</span>Team</span>
				</span> and
				<span class="mention" data-id="Unknown Team" data-value="Unknown Team" data-is-group="true"
				data-denotation-char="@">
					<span><span class="ql-mention-denotation-char">@</span>Unknown Team</span>
				</span><!-- this should be ignored-->
				please check
			</div>
		"""
		self.assertListEqual(extract_mentions(comment), ["test@example.com", "test1@example.com"])

	@change_settings("System Settings", commit=True, password_reset_limit=1)
	def test_rate_limiting_for_reset_password(self):
		url = get_url()
		data = {"cmd": "kanivin.core.doctype.user.user.reset_password", "user": "test@test.com"}

		# Clear rate limit tracker to start fresh
		key = f"rl:{data['cmd']}:{data['user']}"
		kanivin.cache.delete(key)

		c = KanivinClient(url)
		res1 = c.session.post(url, data=data, verify=c.verify, headers=c.headers)
		res2 = c.session.post(url, data=data, verify=c.verify, headers=c.headers)
		self.assertEqual(res1.status_code, 404)
		self.assertEqual(res2.status_code, 429)

	def test_user_rename(self):
		old_name = "test_user_rename@example.com"
		new_name = "test_user_rename_new@example.com"
		user = kanivin.get_doc(
			{
				"doctype": "User",
				"email": old_name,
				"enabled": 1,
				"first_name": "_Test",
				"new_password": "Eastern_43A1W",
				"roles": [{"doctype": "Has Role", "parentfield": "roles", "role": "System Manager"}],
			}
		).insert(ignore_permissions=True, ignore_if_duplicate=True)

		kanivin.rename_doc("User", user.name, new_name)
		self.assertTrue(kanivin.db.exists("Notification Settings", new_name))

		kanivin.delete_doc("User", new_name)

	def test_signup(self):
		import kanivin.website.utils

		random_user = kanivin.mock("email")
		random_user_name = kanivin.mock("name")
		# disabled signup
		with patch.object(user_module, "is_signup_disabled", return_value=True):
			self.assertRaisesRegex(
				kanivin.exceptions.ValidationError,
				"Sign Up is disabled",
				sign_up,
				random_user,
				random_user_name,
				"/signup",
			)

		self.assertTupleEqual(
			sign_up(random_user, random_user_name, "/welcome"),
			(1, "Please check your email for verification"),
		)
		self.assertEqual(kanivin.cache.hget("redirect_after_login", random_user), "/welcome")

		# re-register
		self.assertTupleEqual(sign_up(random_user, random_user_name, "/welcome"), (0, "Already Registered"))

		# disabled user
		user = kanivin.get_doc("User", random_user)
		user.enabled = 0
		user.save()

		self.assertTupleEqual(
			sign_up(random_user, random_user_name, "/welcome"), (0, "Registered but disabled")
		)

		# throttle user creation
		with patch.object(user_module.kanivin.db, "get_creation_count", return_value=301):
			self.assertRaisesRegex(
				kanivin.exceptions.ValidationError,
				"Throttled",
				sign_up,
				kanivin.mock("email"),
				random_user_name,
				"/signup",
			)

	@change_settings("System Settings", password_reset_limit=6)
	def test_reset_password(self):
		from kanivin.auth import CookieManager, LoginManager
		from kanivin.utils import set_request

		old_password = "Eastern_43A1W"
		new_password = "easy_password"

		set_request(path="/random")
		kanivin.local.cookie_manager = CookieManager()
		kanivin.local.login_manager = LoginManager()
		# used by rate limiter when calling reset_password
		kanivin.local.request_ip = "127.0.0.69"

		kanivin.set_user("testpassword@example.com")
		test_user = kanivin.get_doc("User", "testpassword@example.com")
		key = self.reset_password(test_user)
		self.assertEqual(update_password(new_password, key=key), "/app")
		self.assertEqual(
			update_password(new_password, key="wrong_key"),
			"The reset password link has either been used before or is invalid",
		)

		# password verification should fail with old password
		self.assertRaises(kanivin.exceptions.AuthenticationError, verify_password, old_password)
		verify_password(new_password)

		# reset password
		update_password(old_password, old_password=new_password)
		self.assertRaises(TypeError, update_password, "test", 1, ["like", "%"])

		password_strength_response = {
			"feedback": {"password_policy_validation_passed": False, "suggestions": ["Fix password"]}
		}

		# password strength failure test
		with patch.object(user_module, "test_password_strength", return_value=password_strength_response):
			self.assertRaisesRegex(
				kanivin.exceptions.ValidationError,
				"Fix password",
				update_password,
				new_password,
				0,
				test_user.reset_password_key,
			)

		# test redirect URL for website users
		kanivin.set_user("test2@example.com")
		self.assertEqual(update_password(new_password, old_password=old_password), "me")
		# reset password
		update_password(old_password, old_password=new_password)

		# test API endpoint
		with patch.object(user_module.kanivin, "sendmail") as sendmail:
			kanivin.clear_messages()
			test_user = kanivin.get_doc("User", "test2@example.com")
			self.assertEqual(reset_password(user="test2@example.com"), None)
			test_user.reload()
			link = sendmail.call_args_list[0].kwargs["args"]["link"]
			key = parse_qs(urlparse(link).query)["key"][0]
			self.assertEqual(update_password(new_password, key=key), "me")
			update_password(old_password, old_password=new_password)
			self.assertEqual(
				kanivin.message_log[0].get("message"),
				"Password reset instructions have been sent to your email",
			)

		sendmail.assert_called_once()
		self.assertEqual(sendmail.call_args[1]["recipients"], "test2@example.com")

		self.assertEqual(reset_password(user="test2@example.com"), None)
		self.assertEqual(reset_password(user="Administrator"), "not allowed")
		self.assertEqual(reset_password(user="random"), "not found")

	def test_user_onload_modules(self):
		from kanivin.config import get_modules_from_all_apps
		from kanivin.desk.form.load import getdoc

		kanivin.response.docs = []
		getdoc("User", "Administrator")
		doc = kanivin.response.docs[0]
		self.assertListEqual(
			sorted(doc.get("__onload").get("all_modules", [])),
			sorted(m.get("module_name") for m in get_modules_from_all_apps()),
		)

	@change_settings("System Settings", reset_password_link_expiry_duration=1)
	def test_reset_password_link_expiry(self):
		new_password = "new_password"
		kanivin.set_user("testpassword@example.com")
		test_user = kanivin.get_doc("User", "testpassword@example.com")
		key = self.reset_password(test_user)
		time.sleep(1)

		self.assertEqual(
			update_password(new_password, key=key),
			"The reset password link has been expired",
		)


class TestImpersonation(KanivinAPITestCase):
	def test_impersonation(self):
		with test_user(roles=["System Manager"], commit=True) as user:
			self.post(
				self.method("kanivin.core.doctype.user.user.impersonate"),
				{"user": user.name, "reason": "test", "sid": self.sid},
			)
			resp = self.get(self.method("kanivin.auth.get_logged_user"))
			self.assertEqual(resp.json["message"], user.name)


@contextmanager
def test_user(
	*, first_name: str | None = None, email: str | None = None, roles: list[str], commit=False, **kwargs
):
	try:
		first_name = first_name or kanivin.generate_hash()
		email = email or (first_name + "@example.com")
		user: User = kanivin.new_doc(
			"User",
			send_welcome_email=0,
			email=email,
			first_name=first_name,
			**kwargs,
		)
		user.append_roles(*roles)
		user.insert()
		yield user
	finally:
		user.delete(force=True, ignore_permissions=True)
		commit and kanivin.db.commit()


def delete_contact(user):
	kanivin.db.delete("Contact", {"email_id": user})
	kanivin.db.delete("Contact Email", {"email_id": user})
