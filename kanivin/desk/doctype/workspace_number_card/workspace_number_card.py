# Copyright (c) 2023, Kanivin and contributors
# For license information, please see license.txt

# import kanivin
from kanivin.model.document import Document


class WorkspaceNumberCard(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from kanivin.types import DF

		label: DF.Data | None
		number_card_name: DF.Link
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types
	pass
