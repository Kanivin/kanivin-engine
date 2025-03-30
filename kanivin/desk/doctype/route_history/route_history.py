# Copyright (c) 2025, Kanivin and contributors
# License: MIT. See LICENSE

import kanivin
from kanivin.deferred_insert import deferred_insert as _deferred_insert
from kanivin.model.document import Document


class RouteHistory(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from kanivin.types import DF

		route: DF.Data | None
		user: DF.Link | None
	# end: auto-generated types

	@staticmethod
	def clear_old_logs(days=30):
		from kanivin.query_builder import Interval
		from kanivin.query_builder.functions import Now

		table = kanivin.qb.DocType("Route History")
		kanivin.db.delete(table, filters=(table.modified < (Now() - Interval(days=days))))


@kanivin.whitelist()
def deferred_insert(routes):
	routes = [
		{
			"user": kanivin.session.user,
			"route": route.get("route"),
			"creation": route.get("creation"),
		}
		for route in kanivin.parse_json(routes)
	]

	_deferred_insert("Route History", routes)


@kanivin.whitelist()
def frequently_visited_links():
	return kanivin.get_all(
		"Route History",
		fields=["route", "count(name) as count"],
		filters={"user": kanivin.session.user},
		group_by="route",
		order_by="count desc",
		limit=5,
	)
