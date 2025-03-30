# Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import kanivin
from kanivin.desk.form.linked_with import get_linked_docs, get_linked_doctypes
from kanivin.tests.utils import KanivinTestCase


class TestForm(KanivinTestCase):
	def test_linked_with(self):
		results = get_linked_docs("Role", "System Manager", linkinfo=get_linked_doctypes("Role"))
		self.assertTrue("User" in results)
		self.assertTrue("DocType" in results)
