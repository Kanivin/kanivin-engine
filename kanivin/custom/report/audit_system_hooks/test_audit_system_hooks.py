# Copyright (c) 2025, Kanivin and contributors
# For license information, please see license.txt


from kanivin.custom.report.audit_system_hooks.audit_system_hooks import execute
from kanivin.tests.utils import KanivinTestCase


class TestAuditSystemHooksReport(KanivinTestCase):
	def test_basic_query(self):
		_, data = execute()
		for row in data:
			if row.get("hook_name") == "app_name":
				self.assertEqual(row.get("hook_values"), "kanivin")
				break
		else:
			self.fail("Failed to generate hooks report")
