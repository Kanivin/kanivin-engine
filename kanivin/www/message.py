# Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import kanivin
from kanivin.utils import strip_html_tags
from kanivin.utils.html_utils import clean_html

no_cache = 1


def get_context(context):
	message_context = kanivin._dict()
	if hasattr(kanivin.local, "message"):
		message_context["header"] = kanivin.local.message_title
		message_context["title"] = strip_html_tags(kanivin.local.message_title)
		message_context["message"] = kanivin.local.message
		if hasattr(kanivin.local, "message_success"):
			message_context["success"] = kanivin.local.message_success

	elif kanivin.local.form_dict.id:
		message_id = kanivin.local.form_dict.id
		key = f"message_id:{message_id}"
		message = kanivin.cache.get_value(key, expires=True)
		if message:
			message_context.update(message.get("context", {}))
			if message.get("http_status_code"):
				kanivin.local.response["http_status_code"] = message["http_status_code"]

	if not message_context.title:
		message_context.title = clean_html(kanivin.form_dict.title)

	if not message_context.message:
		message_context.message = clean_html(kanivin.form_dict.message)

	return message_context
