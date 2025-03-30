# Copyright (c) 2019, Kanivin and contributors
# License: MIT. See LICENSE

import kanivin
from kanivin.model.document import Document
from kanivin.query_builder import Interval
from kanivin.query_builder.functions import Now


class ScheduledJobLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from kanivin.types import DF

		debug_log: DF.Code | None
		details: DF.Code | None
		scheduled_job_type: DF.Link
		status: DF.Literal["Scheduled", "Complete", "Failed"]

	# end: auto-generated types
	@staticmethod
	def clear_old_logs(days=90):
		table = kanivin.qb.DocType("Scheduled Job Log")
		kanivin.db.delete(table, filters=(table.modified < (Now() - Interval(days=days))))
