# Copyright (c) 2019, Kanivin and contributors
# License: MIT. See LICENSE

# import kanivin
from kanivin.model.document import Document


class ContactEmail(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from kanivin.types import DF

		email_id: DF.Data
		is_primary: DF.Check
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types
	pass
