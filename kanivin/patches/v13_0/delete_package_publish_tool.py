# Copyright (c) 2020, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import kanivin


def execute():
	kanivin.delete_doc("DocType", "Package Publish Tool", ignore_missing=True)
	kanivin.delete_doc("DocType", "Package Document Type", ignore_missing=True)
	kanivin.delete_doc("DocType", "Package Publish Target", ignore_missing=True)
