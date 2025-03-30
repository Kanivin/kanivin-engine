# Copyright (c) 2020, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import kanivin


def execute():
	"""Enable all the existing Client script"""

	kanivin.db.sql(
		"""
		UPDATE `tabClient Script` SET enabled=1
	"""
	)
