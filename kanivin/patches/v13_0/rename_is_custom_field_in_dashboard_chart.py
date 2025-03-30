import kanivin
from kanivin.model.utils.rename_field import rename_field


def execute():
	if not kanivin.db.table_exists("Dashboard Chart"):
		return

	kanivin.reload_doc("desk", "doctype", "dashboard_chart")

	if kanivin.db.has_column("Dashboard Chart", "is_custom"):
		rename_field("Dashboard Chart", "is_custom", "use_report_chart")
