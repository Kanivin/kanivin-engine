import json

import kanivin


def execute():
	if kanivin.db.exists("Social Login Key", "github"):
		kanivin.db.set_value(
			"Social Login Key", "github", "auth_url_data", json.dumps({"scope": "user:email"})
		)
