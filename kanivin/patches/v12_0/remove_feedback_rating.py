import kanivin


def execute():
	"""
	Deprecate Feedback Trigger and Rating. This feature was not customizable.
	Now can be achieved via custom Web Forms
	"""
	kanivin.delete_doc("DocType", "Feedback Trigger")
	kanivin.delete_doc("DocType", "Feedback Rating")
