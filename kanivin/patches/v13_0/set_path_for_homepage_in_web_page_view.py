import kanivin


def execute():
	kanivin.reload_doc("website", "doctype", "web_page_view", force=True)
	kanivin.db.sql("""UPDATE `tabWeb Page View` set path='/' where path=''""")
