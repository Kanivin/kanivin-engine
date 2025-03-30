# Copyright (c) 2024, Kanivin and Contributors
# See license.txt

import kanivin
from kanivin.tests.utils import KanivinTestCase


class TestSystemHealthReport(KanivinTestCase):
	def test_it_works(self):
		kanivin.get_doc("System Health Report")
