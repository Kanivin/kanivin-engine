# Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import kanivin
from kanivin.tests.utils import KanivinTestCase

test_records = kanivin.get_test_records("Page")


class TestPage(KanivinTestCase):
	def test_naming(self):
		self.assertRaises(
			kanivin.NameError,
			kanivin.get_doc(dict(doctype="Page", page_name="DocType", module="Core")).insert,
		)
