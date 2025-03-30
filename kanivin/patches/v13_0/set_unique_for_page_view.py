import kanivin


def execute():
	kanivin.reload_doc("website", "doctype", "web_page_view", force=True)
	site_url = kanivin.utils.get_site_url(kanivin.local.site)
	kanivin.db.sql(f"""UPDATE `tabWeb Page View` set is_unique=1 where referrer LIKE '%{site_url}%'""")
