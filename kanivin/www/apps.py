# Copyright (c) 2023, Kanivin Pvt. Ltd. and Contributors
# MIT License. See license.txt

import kanivin
from kanivin import _
from kanivin.apps import get_apps


def get_context():
	all_apps = get_apps()

	system_default_app = kanivin.get_system_settings("default_app")
	user_default_app = kanivin.db.get_value("User", kanivin.session.user, "default_app")
	default_app = user_default_app if user_default_app else system_default_app

	if len(all_apps) == 0:
		kanivin.local.flags.redirect_location = "/app"
		raise kanivin.Redirect

	for app in all_apps:
		app["is_default"] = True if app.get("name") == default_app else False

	return {"apps": all_apps}
