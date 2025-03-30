import kanivin
from kanivin.model.rename_doc import rename_doc


def execute():
	if kanivin.db.exists("DocType", "Client Script"):
		return

	kanivin.flags.ignore_route_conflict_validation = True
	rename_doc("DocType", "Custom Script", "Client Script")
	kanivin.flags.ignore_route_conflict_validation = False

	kanivin.reload_doctype("Client Script", force=True)
