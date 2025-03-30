import kanivin


def execute():
	categories = kanivin.get_list("Blog Category")
	for category in categories:
		doc = kanivin.get_doc("Blog Category", category["name"])
		doc.set_route()
		doc.save()
