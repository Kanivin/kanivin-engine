# Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import kanivin


def get(name):
	"""
	Return the :term:`doclist` of the `Page` specified by `name`
	"""
	page = kanivin.get_doc("Page", name)
	if page.is_permitted():
		page.load_assets()
		docs = kanivin._dict(page.as_dict())
		if getattr(page, "_dynamic_page", None):
			docs["_dynamic_page"] = 1

		return docs
	else:
		kanivin.response["403"] = 1
		raise kanivin.PermissionError("No read permission for Page %s" % (page.title or name))


@kanivin.whitelist(allow_guest=True)
def getpage(name: str):
	"""
	Load the page from `kanivin.form` and send it via `kanivin.response`
	"""

	doc = get(name)
	kanivin.response.docs.append(doc)
