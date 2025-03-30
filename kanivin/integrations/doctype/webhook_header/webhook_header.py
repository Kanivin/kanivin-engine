# Copyright (c) 2017, Kanivin and contributors
# License: MIT. See LICENSE

# import kanivin
from kanivin.model.document import Document


class WebhookHeader(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from kanivin.types import DF

		key: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		value: DF.Data | None
	# end: auto-generated types
	pass
