# Copyright (c) 2017, Kanivin and contributors
# License: MIT. See LICENSE

import frappe
from frappe.model.document import Document


class PrintHeading(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		description: DF.SmallText | None
		print_heading: DF.Data
	# end: auto-generated types
	pass
