import kanivin


def execute():
	kanivin.delete_doc_if_exists("DocType", "Post")
	kanivin.delete_doc_if_exists("DocType", "Post Comment")
