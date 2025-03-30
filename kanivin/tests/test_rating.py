import kanivin
from kanivin.core.doctype.doctype.test_doctype import new_doctype
from kanivin.tests.utils import KanivinTestCase


class TestRating(KanivinTestCase):
	def setUp(self):
		doc = new_doctype(
			fields=[
				{
					"fieldname": "rating",
					"fieldtype": "Rating",
					"label": "rating",
					"reqd": 1,  # mandatory
				},
			],
		)
		doc.insert()
		self.doctype_name = doc.name

	def test_negative_rating(self):
		doc = kanivin.new_doc(doctype=self.doctype_name, rating=-1)
		doc.insert()
		self.assertEqual(doc.rating, 0)

	def test_positive_rating(self):
		doc = kanivin.new_doc(doctype=self.doctype_name, rating=5)
		doc.insert()
		self.assertEqual(doc.rating, 1)
