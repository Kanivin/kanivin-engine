import kanivin
from kanivin.model.rename_doc import rename_doc


def execute():
	if kanivin.db.table_exists("Workflow Action") and not kanivin.db.table_exists("Workflow Action Master"):
		rename_doc("DocType", "Workflow Action", "Workflow Action Master")
		kanivin.reload_doc("workflow", "doctype", "workflow_action_master")
