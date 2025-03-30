# Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import kanivin

sitemap = 1


def get_context(context):
	context.doc = kanivin.get_cached_doc("About Us Settings")

	return context
