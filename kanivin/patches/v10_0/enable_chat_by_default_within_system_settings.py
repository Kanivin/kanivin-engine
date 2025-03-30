import kanivin


def execute():
	kanivin.reload_doctype("System Settings")
	doc = kanivin.get_single("System Settings")
	doc.enable_chat = 1

	# Changes prescribed by Nabin Hait (nabin@kanivin.io)
	doc.flags.ignore_mandatory = True
	doc.flags.ignore_permissions = True

	doc.save()
