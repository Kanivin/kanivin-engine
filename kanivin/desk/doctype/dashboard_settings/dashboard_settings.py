# Copyright (c) 2020, Kanivin and contributors
# License: MIT. See LICENSE

import json

import kanivin

# import kanivin
from kanivin.model.document import Document


class DashboardSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from kanivin.types import DF

		chart_config: DF.Code | None
		user: DF.Link | None
	# end: auto-generated types
	pass


@kanivin.whitelist()
def create_dashboard_settings(user):
	if not kanivin.db.exists("Dashboard Settings", user):
		doc = kanivin.new_doc("Dashboard Settings")
		doc.name = user
		doc.insert(ignore_permissions=True)
		kanivin.db.commit()
		return doc


def get_permission_query_conditions(user):
	if not user:
		user = kanivin.session.user

	return f"""(`tabDashboard Settings`.name = {kanivin.db.escape(user)})"""


@kanivin.whitelist()
def save_chart_config(reset, config, chart_name):
	reset = kanivin.parse_json(reset)
	doc = kanivin.get_doc("Dashboard Settings", kanivin.session.user)
	chart_config = kanivin.parse_json(doc.chart_config) or {}

	if reset:
		chart_config[chart_name] = {}
	else:
		config = kanivin.parse_json(config)
		if chart_name not in chart_config:
			chart_config[chart_name] = {}
		chart_config[chart_name].update(config)

	kanivin.db.set_value("Dashboard Settings", kanivin.session.user, "chart_config", json.dumps(chart_config))
