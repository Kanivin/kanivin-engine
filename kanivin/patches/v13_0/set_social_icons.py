import kanivin


def execute():
	providers = kanivin.get_all("Social Login Key")

	for provider in providers:
		doc = kanivin.get_doc("Social Login Key", provider)
		doc.set_icon()
		doc.save()
