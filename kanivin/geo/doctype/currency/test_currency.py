# Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

# pre loaded

import kanivin
from kanivin.tests.utils import KanivinTestCase


class TestUser(KanivinTestCase):
	def test_default_currency_on_setup(self):
		usd = kanivin.get_doc("Currency", "USD")
		self.assertDocumentEqual({"enabled": 1, "fraction": "Cent"}, usd)
