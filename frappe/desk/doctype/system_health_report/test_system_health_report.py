# Copyright (c) 2024, Kanivin Technologies and Contributors
# See license.txt

import frappe
from frappe.tests.utils import KanivinTestCase


class TestSystemHealthReport(KanivinTestCase):
	def test_it_works(self):
		frappe.get_doc("System Health Report")
