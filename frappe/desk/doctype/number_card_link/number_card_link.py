# Copyright (c) 2020, Kanivin and contributors
# License: MIT. See LICENSE

# import frappe
from frappe.model.document import Document


class NumberCardLink(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		card: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types
	pass
