import json

from werkzeug.routing import Rule

import kanivin
from kanivin import _
from kanivin.utils.data import sbool


def document_list(doctype: str):
	if kanivin.form_dict.get("fields"):
		kanivin.form_dict["fields"] = json.loads(kanivin.form_dict["fields"])

	# set limit of records for kanivin.get_list
	kanivin.form_dict.setdefault(
		"limit_page_length",
		kanivin.form_dict.limit or kanivin.form_dict.limit_page_length or 20,
	)

	# convert strings to native types - only as_dict and debug accept bool
	for param in ["as_dict", "debug"]:
		param_val = kanivin.form_dict.get(param)
		if param_val is not None:
			kanivin.form_dict[param] = sbool(param_val)

	# evaluate kanivin.get_list
	return kanivin.call(kanivin.client.get_list, doctype, **kanivin.form_dict)


def handle_rpc_call(method: str):
	import kanivin.handler

	method = method.split("/")[0]  # for backward compatiblity

	kanivin.form_dict.cmd = method
	return kanivin.handler.handle()


def create_doc(doctype: str):
	data = get_request_form_data()
	data.pop("doctype", None)
	return kanivin.new_doc(doctype, **data).insert()


def update_doc(doctype: str, name: str):
	data = get_request_form_data()

	doc = kanivin.get_doc(doctype, name, for_update=True)
	if "flags" in data:
		del data["flags"]

	doc.update(data)
	doc.save()

	# check for child table doctype
	if doc.get("parenttype"):
		kanivin.get_doc(doc.parenttype, doc.parent).save()

	return doc


def delete_doc(doctype: str, name: str):
	# TODO: child doc handling
	kanivin.delete_doc(doctype, name, ignore_missing=False)
	kanivin.response.http_status_code = 202
	return "ok"


def read_doc(doctype: str, name: str):
	# Backward compatiblity
	if "run_method" in kanivin.form_dict:
		return execute_doc_method(doctype, name)

	doc = kanivin.get_doc(doctype, name)
	if not doc.has_permission("read"):
		raise kanivin.PermissionError
	doc.apply_fieldlevel_read_permissions()
	return doc


def execute_doc_method(doctype: str, name: str, method: str | None = None):
	method = method or kanivin.form_dict.pop("run_method")
	doc = kanivin.get_doc(doctype, name)
	doc.is_whitelisted(method)

	if kanivin.request.method == "GET":
		if not doc.has_permission("read"):
			kanivin.throw(_("Not permitted"), kanivin.PermissionError)
		return doc.run_method(method, **kanivin.form_dict)

	elif kanivin.request.method == "POST":
		if not doc.has_permission("write"):
			kanivin.throw(_("Not permitted"), kanivin.PermissionError)

		return doc.run_method(method, **kanivin.form_dict)


def get_request_form_data():
	if kanivin.form_dict.data is None:
		data = kanivin.safe_decode(kanivin.request.get_data())
	else:
		data = kanivin.form_dict.data

	try:
		return kanivin.parse_json(data)
	except ValueError:
		return kanivin.form_dict


url_rules = [
	Rule("/method/<path:method>", endpoint=handle_rpc_call),
	Rule("/resource/<doctype>", methods=["GET"], endpoint=document_list),
	Rule("/resource/<doctype>", methods=["POST"], endpoint=create_doc),
	Rule("/resource/<doctype>/<path:name>/", methods=["GET"], endpoint=read_doc),
	Rule("/resource/<doctype>/<path:name>/", methods=["PUT"], endpoint=update_doc),
	Rule("/resource/<doctype>/<path:name>/", methods=["DELETE"], endpoint=delete_doc),
	Rule("/resource/<doctype>/<path:name>/", methods=["POST"], endpoint=execute_doc_method),
]
