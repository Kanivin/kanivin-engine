import kanivin


def execute():
	kanivin.delete_doc_if_exists("DocType", "Web View")
	kanivin.delete_doc_if_exists("DocType", "Web View Component")
	kanivin.delete_doc_if_exists("DocType", "CSS Class")
