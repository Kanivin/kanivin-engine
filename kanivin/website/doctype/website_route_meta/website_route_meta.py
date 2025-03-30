# Copyright (c) 2019, Kanivin and contributors
# License: MIT. See LICENSE

from kanivin.model.document import Document


class WebsiteRouteMeta(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from kanivin.types import DF
		from kanivin.website.doctype.website_meta_tag.website_meta_tag import WebsiteMetaTag

		meta_tags: DF.Table[WebsiteMetaTag]

	# end: auto-generated types
	def autoname(self):
		if self.name and self.name.startswith("/"):
			self.name = self.name[1:]
