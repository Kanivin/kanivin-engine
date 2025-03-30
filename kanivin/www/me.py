# Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import kanivin
import kanivin.www.list
from kanivin import _

no_cache = 1


def get_context(context):
	if kanivin.session.user == "Guest":
		kanivin.throw(_("You need to be logged in to access this page"), kanivin.PermissionError)

	context.current_user = kanivin.get_doc("User", kanivin.session.user)
	context.show_sidebar = True
