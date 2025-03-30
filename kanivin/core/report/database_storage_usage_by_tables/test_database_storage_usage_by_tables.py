# Copyright (c) 2025, Kanivin and contributors
# For license information, please see license.txt


from kanivin.core.report.database_storage_usage_by_tables.database_storage_usage_by_tables import (
	execute,
)
from kanivin.tests.utils import KanivinTestCase


class TestDBUsageReport(KanivinTestCase):
	def test_basic_query(self):
		_, data = execute()
		tables = [d.table for d in data]
		self.assertFalse({"tabUser", "tabDocField"}.difference(tables))
