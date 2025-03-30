import kanivin


def execute():
	kanivin.reload_doctype("Letter Head")

	# source of all existing letter heads must be HTML
	kanivin.db.sql("update `tabLetter Head` set source = 'HTML'")
