import json

import kanivin


def execute():
	"""Handle introduction of UI tours"""
	completed = {}
	for tour in kanivin.get_all("Form Tour", {"ui_tour": 1}, pluck="name"):
		completed[tour] = {"is_complete": True}

	User = kanivin.qb.DocType("User")
	kanivin.qb.update(User).set("onboarding_status", json.dumps(completed)).run()
