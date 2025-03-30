# Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import os

no_cache = 1

import json
import re
from urllib.parse import urlencode

import kanivin
import kanivin.sessions
from kanivin import _
from kanivin.utils.jinja_globals import is_rtl

SCRIPT_TAG_PATTERN = re.compile(r"\<script[^<]*\</script\>")
CLOSING_SCRIPT_TAG_PATTERN = re.compile(r"</script\>")


def get_context(context):
	if kanivin.session.user == "Guest":
		kanivin.response["status_code"] = 403
		kanivin.msgprint(_("Log in to access this page."))
		kanivin.redirect(f"/login?{urlencode({'redirect-to': kanivin.request.path})}")
	elif kanivin.db.get_value("User", kanivin.session.user, "user_type", order_by=None) == "Website User":
		kanivin.throw(_("You are not permitted to access this page."), kanivin.PermissionError)

	hooks = kanivin.get_hooks()
	try:
		boot = kanivin.sessions.get()
	except Exception as e:
		raise kanivin.SessionBootFailed from e

	# this needs commit
	csrf_token = kanivin.sessions.get_csrf_token()

	kanivin.db.commit()

	boot_json = kanivin.as_json(boot, indent=None, separators=(",", ":"))

	# remove script tags from boot
	boot_json = SCRIPT_TAG_PATTERN.sub("", boot_json)

	# TODO: Find better fix
	boot_json = CLOSING_SCRIPT_TAG_PATTERN.sub("", boot_json)

	include_js = hooks.get("app_include_js", []) + kanivin.conf.get("app_include_js", [])
	include_css = hooks.get("app_include_css", []) + kanivin.conf.get("app_include_css", [])
	include_icons = hooks.get("app_include_icons", [])
	kanivin.local.preload_assets["icons"].extend(include_icons)

	if kanivin.get_system_settings("enable_telemetry") and os.getenv("FRAPPE_SENTRY_DSN"):
		include_js.append("sentry.bundle.js")

	context.update(
		{
			"no_cache": 1,
			"build_version": kanivin.utils.get_build_version(),
			"include_js": include_js,
			"include_css": include_css,
			"include_icons": include_icons,
			"layout_direction": "rtl" if is_rtl() else "ltr",
			"lang": kanivin.local.lang,
			"sounds": hooks["sounds"],
			"boot": boot if context.get("for_mobile") else json.loads(boot_json),
			"desk_theme": boot.get("desk_theme") or "Light",
			"csrf_token": csrf_token,
			"google_analytics_id": kanivin.conf.get("google_analytics_id"),
			"google_analytics_anonymize_ip": kanivin.conf.get("google_analytics_anonymize_ip"),
			"app_name": (
				kanivin.get_website_settings("app_name") or kanivin.get_system_settings("app_name") or "Kanivin"
			),
		}
	)

	return context
