# Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

from urllib.parse import parse_qsl

import kanivin
from kanivin import _
from kanivin.twofactor import get_qr_svg_code


def get_context(context):
	context.no_cache = 1
	context.qr_code_user, context.qrcode_svg = get_user_svg_from_cache()


def get_query_key():
	"""Return query string arg."""
	query_string = kanivin.local.request.query_string
	query = dict(parse_qsl(query_string))
	query = {key.decode(): val.decode() for key, val in query.items()}
	if "k" not in list(query):
		kanivin.throw(_("Not Permitted"), kanivin.PermissionError)
	query = (query["k"]).strip()
	if False in [i.isalpha() or i.isdigit() for i in query]:
		kanivin.throw(_("Not Permitted"), kanivin.PermissionError)
	return query


def get_user_svg_from_cache():
	"""Get User and SVG code from cache."""
	key = get_query_key()
	totp_uri = kanivin.cache.get_value(f"{key}_uri")
	user = kanivin.cache.get_value(f"{key}_user")
	if not totp_uri or not user:
		kanivin.throw(_("Page has expired!"), kanivin.PermissionError)
	if not kanivin.db.exists("User", user):
		kanivin.throw(_("Not Permitted"), kanivin.PermissionError)
	user = kanivin.get_doc("User", user)
	svg = get_qr_svg_code(totp_uri)
	return (user, svg.decode())
