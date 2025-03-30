# Copyright (c) 2018, Kanivin and contributors
# License: MIT. See LICENSE

import kanivin
from kanivin.model.document import Document


class ViewLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from kanivin.types import DF

		reference_doctype: DF.Link | None
		reference_name: DF.DynamicLink | None
		viewed_by: DF.Data | None

	# end: auto-generated types
	@staticmethod
	def clear_old_logs(days=180):
		from kanivin.query_builder import Interval
		from kanivin.query_builder.functions import Now

		table = kanivin.qb.DocType("View Log")
		kanivin.db.delete(table, filters=(table.modified < (Now() - Interval(days=days))))
