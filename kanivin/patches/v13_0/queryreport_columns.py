# Copyright (c) 2021, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import json

import kanivin


def execute():
	"""Convert Query Report json to support other content"""
	records = kanivin.get_all("Report", filters={"json": ["!=", ""]}, fields=["name", "json"])
	for record in records:
		jstr = record["json"]
		data = json.loads(jstr)
		if isinstance(data, list):
			# double escape braces
			jstr = f'{{"columns":{jstr}}}'
			kanivin.db.set_value("Report", record["name"], "json", jstr)
