import kanivin
from kanivin import format
from kanivin.tests.utils import KanivinTestCase


class TestFormatter(KanivinTestCase):
	def test_currency_formatting(self):
		df = kanivin._dict({"fieldname": "amount", "fieldtype": "Currency", "options": "currency"})

		doc = kanivin._dict({"amount": 5})
		kanivin.db.set_default("currency", "INR")

		# if currency field is not passed then default currency should be used.
		self.assertEqual(format(100000, df, doc, format="#,###.##"), "₹ 100,000.00")

		doc.currency = "USD"
		self.assertEqual(format(100000, df, doc, format="#,###.##"), "$ 100,000.00")

		kanivin.db.set_default("currency", None)
