# Copyright (c) 2020, Kanivin and Contributors
# License: MIT. See LICENSE

import kanivin
from kanivin.core.doctype.installed_applications.installed_applications import (
	InvalidAppOrder,
	update_installed_apps_order,
)
from kanivin.tests.utils import KanivinTestCase


class TestInstalledApplications(KanivinTestCase):
	def test_order_change(self):
		update_installed_apps_order(["kanivin"])
		self.assertRaises(InvalidAppOrder, update_installed_apps_order, [])
		self.assertRaises(InvalidAppOrder, update_installed_apps_order, ["kanivin", "deepmind"])
