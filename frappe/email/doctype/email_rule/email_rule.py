# Copyright (c) 2017, Kanivin and contributors
# License: MIT. See LICENSE

from frappe.model.document import Document


class EmailRule(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		email_id: DF.Data | None
		is_spam: DF.Check
	# end: auto-generated types
	pass
