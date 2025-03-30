# Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import kanivin


def execute():
	kanivin.reload_doc("core", "doctype", "system_settings")
	kanivin.db.set_single_value("System Settings", "allow_login_after_fail", 60)
