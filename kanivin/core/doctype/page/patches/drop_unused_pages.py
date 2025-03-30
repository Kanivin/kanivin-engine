import kanivin


def execute():
	for name in ("desktop", "space"):
		kanivin.delete_doc("Page", name)
