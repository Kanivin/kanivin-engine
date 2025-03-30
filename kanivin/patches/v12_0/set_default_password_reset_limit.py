# Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import kanivin


def execute():
	kanivin.reload_doc("core", "doctype", "system_settings", force=1)
	kanivin.db.set_single_value("System Settings", "password_reset_limit", 3)
