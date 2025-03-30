import kanivin
from kanivin.utils.install import create_user_type


def execute():
	kanivin.reload_doc("core", "doctype", "role")
	kanivin.reload_doc("core", "doctype", "user_document_type")
	kanivin.reload_doc("core", "doctype", "user_type_module")
	kanivin.reload_doc("core", "doctype", "user_select_document_type")
	kanivin.reload_doc("core", "doctype", "user_type")

	create_user_type()
