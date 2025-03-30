# Copyright (c) 2020, Kanivin and contributors
# License: MIT. See LICENSE

import json

import kanivin
from kanivin.model.document import Document
from kanivin.utils.safe_exec import read_sql, safe_exec


class SystemConsole(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from kanivin.types import DF

		commit: DF.Check
		console: DF.Code | None
		output: DF.Code | None
		show_processlist: DF.Check
		type: DF.Literal["Python", "SQL"]

	# end: auto-generated types
	def run(self):
		kanivin.only_for("System Manager")
		try:
			kanivin.local.debug_log = []
			if self.type == "Python":
				safe_exec(self.console, script_filename="System Console")
				self.output = "\n".join(kanivin.debug_log)
			elif self.type == "SQL":
				self.output = kanivin.as_json(read_sql(self.console, as_dict=1))
		except Exception:
			self.commit = False
			self.output = kanivin.get_traceback()

		if self.commit:
			kanivin.db.commit()
		else:
			kanivin.db.rollback()
		kanivin.get_doc(
			dict(doctype="Console Log", script=self.console, type=self.type, committed=self.commit)
		).insert()
		kanivin.db.commit()


@kanivin.whitelist()
def execute_code(doc):
	console = kanivin.get_doc(json.loads(doc))
	console.run()
	return console.as_dict()


@kanivin.whitelist()
def show_processlist():
	kanivin.only_for("System Manager")

	return kanivin.db.multisql(
		{
			"postgres": """
			SELECT pid AS "Id",
				query_start AS "Time",
				state AS "State",
				query AS "Info",
				wait_event AS "Progress"
			FROM pg_stat_activity""",
			"mariadb": "show full processlist",
		},
		as_dict=True,
	)
