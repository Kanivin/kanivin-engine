import kanivin


def execute():
	kanivin.reload_doc("workflow", "doctype", "workflow_transition")
	kanivin.db.sql("update `tabWorkflow Transition` set allow_self_approval=1")
