import json

import kanivin


@kanivin.whitelist()
def get_onboarding_status():
	onboarding_status = kanivin.db.get_value("User", kanivin.session.user, "onboarding_status")
	return kanivin.parse_json(onboarding_status) if onboarding_status else {}


@kanivin.whitelist()
def update_user_onboarding_status(steps: str, appName: str):
	steps = json.loads(steps)

	# get the current onboarding status
	onboarding_status = kanivin.db.get_value("User", kanivin.session.user, "onboarding_status")
	onboarding_status = kanivin.parse_json(onboarding_status)

	# update the onboarding status
	onboarding_status[appName + "_onboarding_status"] = steps

	kanivin.db.set_value(
		"User", kanivin.session.user, "onboarding_status", json.dumps(onboarding_status), update_modified=False
	)
