# Copyright (c) 2020, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import kanivin


def execute():
	kanivin.reload_doc("website", "doctype", "website_theme_ignore_app")
	themes = kanivin.get_all("Website Theme", filters={"theme_url": ("not like", "/files/website_theme/%")})
	for theme in themes:
		doc = kanivin.get_doc("Website Theme", theme.name)
		try:
			doc.save()
		except Exception:
			print("Ignoring....")
			print(kanivin.get_traceback())
