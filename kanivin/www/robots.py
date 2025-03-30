import kanivin

base_template_path = "www/robots.txt"


def get_context(context):
	robots_txt = (
		kanivin.db.get_single_value("Website Settings", "robots_txt")
		or (kanivin.local.conf.robots_txt and kanivin.read_file(kanivin.local.conf.robots_txt))
		or ""
	)

	return {"robots_txt": robots_txt}
