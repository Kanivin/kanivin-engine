# Copyright (c) 2017, Kanivin and Contributors
# License: MIT. See LICENSE
import kanivin
from kanivin.tests.utils import KanivinTestCase


class TestLetterHead(KanivinTestCase):
	def test_auto_image(self):
		letter_head = kanivin.get_doc(
			dict(doctype="Letter Head", letter_head_name="Test", source="Image", image="/public/test.png")
		).insert()

		# test if image is automatically set
		self.assertTrue(letter_head.image in letter_head.content)
