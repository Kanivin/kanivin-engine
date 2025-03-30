import re

import kanivin
from kanivin.query_builder import DocType


def execute():
	"""Replace temporarily available Database Aggregate APIs on kanivin (develop)

	APIs changed:
	        * kanivin.db.max => kanivin.qb.max
	        * kanivin.db.min => kanivin.qb.min
	        * kanivin.db.sum => kanivin.qb.sum
	        * kanivin.db.avg => kanivin.qb.avg
	"""
	ServerScript = DocType("Server Script")
	server_scripts = (
		kanivin.qb.from_(ServerScript)
		.where(
			ServerScript.script.like("%kanivin.db.max(%")
			| ServerScript.script.like("%kanivin.db.min(%")
			| ServerScript.script.like("%kanivin.db.sum(%")
			| ServerScript.script.like("%kanivin.db.avg(%")
		)
		.select("name", "script")
		.run(as_dict=True)
	)

	for server_script in server_scripts:
		name, script = server_script["name"], server_script["script"]

		for agg in ["avg", "max", "min", "sum"]:
			script = re.sub(f"kanivin.db.{agg}\\(", f"kanivin.qb.{agg}(", script)

		kanivin.db.set_value("Server Script", name, "script", script)
