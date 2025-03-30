# Copyright (c) 2025, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import kanivin
from kanivin.config import get_modules_from_all_apps_for_user
from kanivin.tests.utils import KanivinTestCase


class TestConfig(KanivinTestCase):
	def test_get_modules(self):
		kanivin_modules = kanivin.get_all("Module Def", filters={"app_name": "kanivin"}, pluck="name")
		all_modules_data = get_modules_from_all_apps_for_user()
		all_modules = [x["module_name"] for x in all_modules_data]
		self.assertIsInstance(all_modules_data, list)
		self.assertFalse([x for x in kanivin_modules if x not in all_modules])
