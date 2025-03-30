# Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import re

import kanivin
from kanivin import _
from kanivin.desk.utils import slug


@kanivin.whitelist()
def get_apps():
	from kanivin.desk.desktop import get_workspace_sidebar_items

	allowed_workspaces = get_workspace_sidebar_items().get("pages")

	apps = kanivin.get_installed_apps()
	app_list = []

	for app in apps:
		if app == "kanivin":
			continue
		app_details = kanivin.get_hooks("add_to_apps_screen", app_name=app)
		if not len(app_details):
			continue
		for app_detail in app_details:
			has_permission_path = app_detail.get("has_permission")
			if has_permission_path and not kanivin.get_attr(has_permission_path)():
				continue
			app_list.append(
				{
					"name": app,
					"logo": app_detail.get("logo"),
					"title": _(app_detail.get("title")),
					"route": get_route(app_detail, allowed_workspaces),
				}
			)
	return app_list


def get_route(app, allowed_workspaces=None):
	if not allowed_workspaces:
		return "/app"

	route = app.get("route") if app and app.get("route") else "/apps"

	# Check if user has access to default workspace, if not, pick first workspace user has access to
	if route.startswith("/app/"):
		ws = route.split("/")[2]

		for allowed_ws in allowed_workspaces:
			if allowed_ws.get("name").lower() == ws.lower():
				return route

		module_app = kanivin.local.module_app
		for allowed_ws in allowed_workspaces:
			module = allowed_ws.get("module")
			if module and module_app.get(module.lower()) == app.get("name"):
				return f"/app/{slug(allowed_ws.name.lower())}"
		return f"/app/{slug(allowed_workspaces[0].get('name').lower())}"
	else:
		return route


def is_desk_apps(apps):
	for app in apps:
		# check if route is /app or /app/* and not /app1 or /app1/*
		pattern = r"^/app(/.*)?$"
		route = app.get("route")
		if route and not re.match(pattern, route):
			return False
	return True


def get_default_path(apps=None):
	if not apps:
		apps = get_apps()
	_apps = [app for app in apps if app.get("name") != "kanivin"]

	if len(_apps) == 0:
		return None

	system_default_app = kanivin.get_system_settings("default_app")
	user_default_app = kanivin.db.get_value("User", kanivin.session.user, "default_app")

	if system_default_app and not user_default_app:
		app = next((app for app in apps if app.get("name") == system_default_app), None)
		return app.get("route") if app else None
	elif user_default_app:
		app = next((app for app in apps if app.get("name") == user_default_app), None)
		return app.get("route") if app else None

	if len(_apps) == 1:
		return _apps[0].get("route") or "/apps"
	elif is_desk_apps(_apps):
		return "/app"
	return "/apps"


@kanivin.whitelist()
def set_app_as_default(app_name):
	if kanivin.db.get_value("User", kanivin.session.user, "default_app") == app_name:
		kanivin.db.set_value("User", kanivin.session.user, "default_app", "")
	else:
		kanivin.db.set_value("User", kanivin.session.user, "default_app", app_name)
