# Copyright (c) 2020, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import kanivin


def execute():
	if kanivin.db.exists("DocType", "Onboarding"):
		kanivin.rename_doc("DocType", "Onboarding", "Module Onboarding", ignore_if_exists=True)
