# Copyright (c) 2021, Kanivin and contributors
# License: MIT. See LICENSE

import kanivin
from kanivin.model.document import Document


class WebhookRequestLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from kanivin.types import DF

		data: DF.Code | None
		error: DF.Text | None
		headers: DF.Code | None
		reference_document: DF.Data | None
		response: DF.Code | None
		url: DF.Text | None
		user: DF.Link | None
		webhook: DF.Link | None

	# end: auto-generated types
	@staticmethod
	def clear_old_logs(days=30):
		from kanivin.query_builder import Interval
		from kanivin.query_builder.functions import Now

		table = kanivin.qb.DocType("Webhook Request Log")
		kanivin.db.delete(table, filters=(table.modified < (Now() - Interval(days=days))))
