import kanivin


def execute():
	if kanivin.db.table_exists("Prepared Report"):
		kanivin.reload_doc("core", "doctype", "prepared_report")
		prepared_reports = kanivin.get_all("Prepared Report")
		for report in prepared_reports:
			kanivin.delete_doc("Prepared Report", report.name)
