import kanivin


def execute():
	kanivin.reload_doc("core", "doctype", "domain")
	kanivin.reload_doc("core", "doctype", "has_domain")
	active_domains = kanivin.get_active_domains()
	all_domains = kanivin.get_all("Domain")

	for d in all_domains:
		if d.name not in active_domains:
			inactive_domain = kanivin.get_doc("Domain", d.name)
			inactive_domain.setup_data()
			inactive_domain.remove_custom_field()
