# Copyright (c) 2015, Kanivin and Contributors
# License: MIT. See LICENSE
import time

import kanivin
from kanivin.auth import CookieManager, LoginManager
from kanivin.tests.utils import KanivinTestCase


class TestActivityLog(KanivinTestCase):
	def setUp(self) -> None:
		kanivin.set_user("Administrator")

	def test_activity_log(self):
		# test user login log
		kanivin.local.form_dict = kanivin._dict(
			{
				"cmd": "login",
				"sid": "Guest",
				"pwd": self.ADMIN_PASSWORD or "admin",
				"usr": "Administrator",
			}
		)

		kanivin.local.request_ip = "127.0.0.1"
		kanivin.local.cookie_manager = CookieManager()
		kanivin.local.login_manager = LoginManager()

		auth_log = self.get_auth_log()
		self.assertFalse(kanivin.form_dict.pwd)
		self.assertEqual(auth_log.status, "Success")

		# test user logout log
		kanivin.local.login_manager.logout()
		auth_log = self.get_auth_log(operation="Logout")
		self.assertEqual(auth_log.status, "Success")

		# test invalid login
		kanivin.form_dict.update({"pwd": "password"})
		self.assertRaises(kanivin.AuthenticationError, LoginManager)
		auth_log = self.get_auth_log()
		self.assertEqual(auth_log.status, "Failed")

		kanivin.local.form_dict = kanivin._dict()

	def get_auth_log(self, operation="Login"):
		names = kanivin.get_all(
			"Activity Log",
			filters={
				"user": "Administrator",
				"operation": operation,
			},
			order_by="`creation` DESC",
		)

		name = names[0]
		return kanivin.get_doc("Activity Log", name)

	def test_brute_security(self):
		update_system_settings({"allow_consecutive_login_attempts": 3, "allow_login_after_fail": 5})

		kanivin.local.form_dict = kanivin._dict(
			{"cmd": "login", "sid": "Guest", "pwd": self.ADMIN_PASSWORD, "usr": "Administrator"}
		)

		kanivin.local.request_ip = "127.0.0.1"
		kanivin.local.cookie_manager = CookieManager()
		kanivin.local.login_manager = LoginManager()

		auth_log = self.get_auth_log()
		self.assertEqual(auth_log.status, "Success")

		# test user logout log
		kanivin.local.login_manager.logout()
		auth_log = self.get_auth_log(operation="Logout")
		self.assertEqual(auth_log.status, "Success")

		# test invalid login
		kanivin.form_dict.update({"pwd": "password"})
		self.assertRaises(kanivin.AuthenticationError, LoginManager)
		self.assertRaises(kanivin.AuthenticationError, LoginManager)
		self.assertRaises(kanivin.AuthenticationError, LoginManager)

		# REMOVE ME: current logic allows allow_consecutive_login_attempts+1 attempts
		# before raising security exception, remove below line when that is fixed.
		self.assertRaises(kanivin.AuthenticationError, LoginManager)
		self.assertRaises(kanivin.SecurityException, LoginManager)
		time.sleep(5)
		self.assertRaises(kanivin.AuthenticationError, LoginManager)

		kanivin.local.form_dict = kanivin._dict()


def update_system_settings(args):
	doc = kanivin.get_doc("System Settings")
	doc.update(args)
	doc.flags.ignore_mandatory = 1
	doc.save()
