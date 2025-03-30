import kanivin
from kanivin.model.naming import append_number_if_name_exists
from kanivin.utils.dashboard import get_dashboards_with_link


def execute():
	if (
		not kanivin.db.table_exists("Dashboard Chart")
		or not kanivin.db.table_exists("Number Card")
		or not kanivin.db.table_exists("Dashboard")
	):
		return

	kanivin.reload_doc("desk", "doctype", "dashboard_chart")
	kanivin.reload_doc("desk", "doctype", "number_card")
	kanivin.reload_doc("desk", "doctype", "dashboard")

	modified_charts = get_modified_docs("Dashboard Chart")
	modified_cards = get_modified_docs("Number Card")
	modified_dashboards = [doc.name for doc in get_modified_docs("Dashboard")]

	for chart in modified_charts:
		modified_dashboards += get_dashboards_with_link(chart.name, "Dashboard Chart")
		rename_modified_doc(chart.name, "Dashboard Chart")

	for card in modified_cards:
		modified_dashboards += get_dashboards_with_link(card.name, "Number Card")
		rename_modified_doc(card.name, "Number Card")

	modified_dashboards = list(set(modified_dashboards))

	for dashboard in modified_dashboards:
		rename_modified_doc(dashboard, "Dashboard")


def get_modified_docs(doctype):
	return kanivin.get_all(doctype, filters={"owner": "Administrator", "modified_by": ["!=", "Administrator"]})


def rename_modified_doc(docname, doctype):
	new_name = docname + " Custom"
	try:
		kanivin.rename_doc(doctype, docname, new_name)
	except kanivin.ValidationError:
		new_name = append_number_if_name_exists(doctype, new_name)
		kanivin.rename_doc(doctype, docname, new_name)
