# Copyright (c) 2019, Kanivin and contributors
# License: MIT. See LICENSE

import os

import kanivin
from kanivin.model.document import Document
from kanivin.modules import get_module_path, scrub
from kanivin.modules.export_file import export_to_files


@kanivin.whitelist()
def get_config(name):
	doc = kanivin.get_doc("Dashboard Chart Source", name)
	with open(
		os.path.join(
			get_module_path(doc.module), "dashboard_chart_source", scrub(doc.name), scrub(doc.name) + ".js"
		),
	) as f:
		return f.read()


class DashboardChartSource(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from kanivin.types import DF

		module: DF.Link
		source_name: DF.Data
		timeseries: DF.Check

	# end: auto-generated types
	def on_update(self):
		export_to_files(record_list=[[self.doctype, self.name]], record_module=self.module, create_init=True)
