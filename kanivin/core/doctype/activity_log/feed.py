# Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import kanivin
import kanivin.permissions
from kanivin import _
from kanivin.core.doctype.activity_log.activity_log import add_authentication_log
from kanivin.utils import get_fullname


def login_feed(login_manager):
	if login_manager.user != "Guest":
		subject = _("{0} logged in").format(get_fullname(login_manager.user))
		add_authentication_log(subject, login_manager.user)


def logout_feed(user, reason):
	if user and user != "Guest":
		subject = _("{0} logged out: {1}").format(get_fullname(user), kanivin.bold(reason))
		add_authentication_log(subject, user, operation="Logout")
