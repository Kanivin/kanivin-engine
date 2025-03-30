# Copyright (c) 2020, Kanivin and contributors
# License: MIT. See LICENSE

from urllib.parse import urlparse

import kanivin
import kanivin.utils
from kanivin.model.document import Document


class WebPageView(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from kanivin.types import DF

		browser: DF.Data | None
		browser_version: DF.Data | None
		campaign: DF.Data | None
		is_unique: DF.Data | None
		medium: DF.Data | None
		path: DF.Data | None
		referrer: DF.Data | None
		source: DF.Data | None
		time_zone: DF.Data | None
		user_agent: DF.Data | None
		visitor_id: DF.Data | None

	# end: auto-generated types
	@staticmethod
	def clear_old_logs(days=180):
		from kanivin.query_builder import Interval
		from kanivin.query_builder.functions import Now

		table = kanivin.qb.DocType("Web Page View")
		kanivin.db.delete(table, filters=(table.modified < (Now() - Interval(days=days))))


@kanivin.whitelist(allow_guest=True)
def make_view_log(
	referrer=None,
	browser=None,
	version=None,
	user_tz=None,
	source=None,
	campaign=None,
	medium=None,
	visitor_id=None,
):
	if not is_tracking_enabled():
		return

	# real path
	path = kanivin.request.headers.get("Referer")

	if not kanivin.utils.is_site_link(path):
		return

	path = urlparse(path).path

	request_dict = kanivin.request.__dict__
	user_agent = request_dict.get("environ", {}).get("HTTP_USER_AGENT")

	if referrer:
		referrer = referrer.split("?", 1)[0]

	if path != "/" and path.startswith("/"):
		path = path[1:]

	if path.startswith(("api/", "app/", "assets/", "private/files/")):
		return

	is_unique = visitor_id and not bool(kanivin.db.exists("Web Page View", {"visitor_id": visitor_id}))

	view = kanivin.new_doc("Web Page View")
	view.path = path
	view.referrer = referrer
	view.browser = browser
	view.browser_version = version
	view.time_zone = user_tz
	view.user_agent = user_agent
	view.is_unique = is_unique
	view.source = source
	view.campaign = campaign
	view.medium = (medium or "").lower()
	view.visitor_id = visitor_id

	try:
		if kanivin.flags.read_only:
			view.deferred_insert()
		else:
			view.insert(ignore_permissions=True)
	except Exception:
		kanivin.clear_last_message()


@kanivin.whitelist()
def get_page_view_count(path):
	return kanivin.db.count("Web Page View", filters={"path": path})


def is_tracking_enabled():
	return kanivin.db.get_single_value("Website Settings", "enable_view_tracking")
