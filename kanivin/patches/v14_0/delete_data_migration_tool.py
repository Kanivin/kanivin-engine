# Copyright (c) 2025, Kanivin Pvt. Ltd. and Contributors
# MIT License. See license.txt

import kanivin


def execute():
	doctypes = kanivin.get_all("DocType", {"module": "Data Migration", "custom": 0}, pluck="name")
	for doctype in doctypes:
		kanivin.delete_doc("DocType", doctype, ignore_missing=True)

	kanivin.delete_doc("Module Def", "Data Migration", ignore_missing=True, force=True)
