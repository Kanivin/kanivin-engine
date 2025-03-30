# Copyright (c) 2015, Kanivin and contributors
# License: MIT. See LICENSE

import kanivin
from kanivin.model.document import Document
from kanivin.query_builder import Interval
from kanivin.query_builder.functions import Now


class ErrorLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from kanivin.types import DF

		error: DF.Code | None
		method: DF.Data | None
		reference_doctype: DF.Link | None
		reference_name: DF.Data | None
		seen: DF.Check
		trace_id: DF.Data | None

	# end: auto-generated types
	def onload(self):
		if not self.seen and not kanivin.flags.read_only:
			self.db_set("seen", 1, update_modified=0)
			kanivin.db.commit()

	@staticmethod
	def clear_old_logs(days=30):
		table = kanivin.qb.DocType("Error Log")
		kanivin.db.delete(table, filters=(table.modified < (Now() - Interval(days=days))))


@kanivin.whitelist()
def clear_error_logs():
	"""Flush all Error Logs"""
	kanivin.only_for("System Manager")
	kanivin.db.truncate("Error Log")
