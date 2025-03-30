import kanivin


def execute():
	item = kanivin.db.exists("Navbar Item", {"item_label": "Background Jobs"})
	if not item:
		return

	kanivin.delete_doc("Navbar Item", item)
