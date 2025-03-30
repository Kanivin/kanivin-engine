# Copyright (c) 2025, Kanivin and Contributors
# License: MIT. See LICENSE


import kanivin
from kanivin.model import data_field_options


def execute():
	custom_field = kanivin.qb.DocType("Custom Field")
	(
		kanivin.qb.update(custom_field)
		.set(custom_field.options, None)
		.where((custom_field.fieldtype == "Data") & (custom_field.options.notin(data_field_options)))
	).run()
