# Copyright (c) 2015, Kanivin and Contributors
# License: MIT. See LICENSE
import kanivin
from kanivin.contacts.doctype.address_template.address_template import get_default_address_template
from kanivin.tests.utils import KanivinTestCase
from kanivin.utils.jinja import validate_template


class TestAddressTemplate(KanivinTestCase):
	def setUp(self) -> None:
		kanivin.db.delete("Address Template", {"country": "India"})
		kanivin.db.delete("Address Template", {"country": "Brazil"})

	def test_default_address_template(self):
		validate_template(get_default_address_template())

	def test_default_is_unset(self):
		kanivin.get_doc({"doctype": "Address Template", "country": "India", "is_default": 1}).insert()

		self.assertEqual(kanivin.db.get_value("Address Template", "India", "is_default"), 1)

		kanivin.get_doc({"doctype": "Address Template", "country": "Brazil", "is_default": 1}).insert()

		self.assertEqual(kanivin.db.get_value("Address Template", "India", "is_default"), 0)
		self.assertEqual(kanivin.db.get_value("Address Template", "Brazil", "is_default"), 1)

	def test_delete_address_template(self):
		india = kanivin.get_doc({"doctype": "Address Template", "country": "India", "is_default": 0}).insert()

		brazil = kanivin.get_doc(
			{"doctype": "Address Template", "country": "Brazil", "is_default": 1}
		).insert()

		india.reload()  # might have been modified by the second template
		india.delete()  # should not raise an error

		self.assertRaises(kanivin.ValidationError, brazil.delete)
