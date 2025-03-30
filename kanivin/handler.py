# Copyright (c) 2025, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import os
from mimetypes import guess_type
from typing import TYPE_CHECKING

from werkzeug.wrappers import Response

import kanivin
import kanivin.sessions
import kanivin.utils
from kanivin import _, is_whitelisted, ping
from kanivin.core.doctype.server_script.server_script_utils import get_server_script_map
from kanivin.monitor import add_data_to_monitor
from kanivin.permissions import check_doctype_permission
from kanivin.utils import cint
from kanivin.utils.csvutils import build_csv_response
from kanivin.utils.deprecations import deprecation_warning
from kanivin.utils.image import optimize_image
from kanivin.utils.response import build_response

if TYPE_CHECKING:
	from kanivin.core.doctype.file.file import File
	from kanivin.core.doctype.user.user import User

ALLOWED_MIMETYPES = (
	"image/png",
	"image/jpeg",
	"application/pdf",
	"application/msword",
	"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
	"application/vnd.ms-excel",
	"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
	"application/vnd.oasis.opendocument.text",
	"application/vnd.oasis.opendocument.spreadsheet",
	"text/plain",
	"video/quicktime",
	"video/mp4",
	"text/csv",
)


def handle():
	"""handle request"""

	cmd = kanivin.local.form_dict.cmd
	data = None

	if cmd != "login":
		data = execute_cmd(cmd)

	# data can be an empty string or list which are valid responses
	if data is not None:
		if isinstance(data, Response):
			# method returns a response object, pass it on
			return data

		# add the response to `message` label
		kanivin.response["message"] = data


def execute_cmd(cmd, from_async=False):
	"""execute a request as python module"""
	cmd = kanivin.override_whitelisted_method(cmd)

	# via server script
	server_script = get_server_script_map().get("_api", {}).get(cmd)
	if server_script:
		return run_server_script(server_script)

	try:
		method = get_attr(cmd)
	except Exception as e:
		kanivin.throw(_("Failed to get method for command {0} with {1}").format(cmd, e))

	if from_async:
		method = method.queue

	if method != run_doc_method:
		is_whitelisted(method)
		is_valid_http_method(method)

	return kanivin.call(method, **kanivin.form_dict)


def run_server_script(server_script):
	response = kanivin.get_doc("Server Script", server_script).execute_method()

	# some server scripts return output using flags (empty dict by default),
	# while others directly modify kanivin.response
	# return flags if not empty dict (this overwrites kanivin.response.message)
	if response != {}:
		return response


def is_valid_http_method(method):
	if kanivin.flags.in_safe_exec:
		return

	http_method = kanivin.local.request.method

	if http_method not in kanivin.allowed_http_methods_for_whitelisted_func[method]:
		throw_permission_error()


def throw_permission_error():
	kanivin.throw(_("Not permitted"), kanivin.PermissionError)


@kanivin.whitelist(allow_guest=True)
def logout():
	kanivin.local.login_manager.logout()
	kanivin.db.commit()


@kanivin.whitelist(allow_guest=True)
def web_logout():
	kanivin.local.login_manager.logout()
	kanivin.db.commit()
	kanivin.respond_as_web_page(
		_("Logged Out"), _("You have been successfully logged out"), indicator_color="green"
	)


@kanivin.whitelist()
def uploadfile():
	deprecation_warning(
		"uploadfile is deprecated and will be removed in v16. Use upload_file instead.",
	)
	ret = None
	check_write_permission(kanivin.form_dict.doctype, kanivin.form_dict.docname)

	try:
		if kanivin.form_dict.get("from_form"):
			try:
				ret = kanivin.get_doc(
					{
						"doctype": "File",
						"attached_to_name": kanivin.form_dict.docname,
						"attached_to_doctype": kanivin.form_dict.doctype,
						"attached_to_field": kanivin.form_dict.docfield,
						"file_url": kanivin.form_dict.file_url,
						"file_name": kanivin.form_dict.filename,
						"is_private": kanivin.utils.cint(kanivin.form_dict.is_private),
						"content": kanivin.form_dict.filedata,
						"decode": True,
					}
				)
				ret.save()
			except kanivin.DuplicateEntryError:
				# ignore pass
				ret = None
				kanivin.db.rollback()
		else:
			if kanivin.form_dict.get("method"):
				method = kanivin.get_attr(kanivin.form_dict.method)
				is_whitelisted(method)
				ret = method()
	except Exception:
		kanivin.errprint(kanivin.utils.get_traceback())
		kanivin.response["http_status_code"] = 500
		ret = None

	return ret


@kanivin.whitelist(allow_guest=True)
def upload_file():
	user = None
	if kanivin.session.user == "Guest":
		if kanivin.get_system_settings("allow_guests_to_upload_files"):
			ignore_permissions = True
		else:
			raise kanivin.PermissionError
	else:
		user: "User" = kanivin.get_doc("User", kanivin.session.user)
		ignore_permissions = False

	files = kanivin.request.files
	is_private = kanivin.form_dict.is_private
	doctype = kanivin.form_dict.doctype
	docname = kanivin.form_dict.docname
	fieldname = kanivin.form_dict.fieldname
	file_url = kanivin.form_dict.file_url
	folder = kanivin.form_dict.folder or "Home"
	method = kanivin.form_dict.method
	filename = kanivin.form_dict.file_name
	optimize = kanivin.form_dict.optimize
	content = None

	if library_file := kanivin.form_dict.get("library_file_name"):
		kanivin.has_permission("File", doc=library_file, throw=True)
		doc = kanivin.get_value(
			"File",
			kanivin.form_dict.library_file_name,
			["is_private", "file_url", "file_name"],
			as_dict=True,
		)
		is_private = doc.is_private
		file_url = doc.file_url
		filename = doc.file_name

	if not ignore_permissions:
		check_write_permission(doctype, docname)

	if "file" in files:
		file = files["file"]
		content = file.stream.read()
		filename = file.filename

		content_type = guess_type(filename)[0]
		if optimize and content_type and content_type.startswith("image/"):
			args = {"content": content, "content_type": content_type}
			if kanivin.form_dict.max_width:
				args["max_width"] = int(kanivin.form_dict.max_width)
			if kanivin.form_dict.max_height:
				args["max_height"] = int(kanivin.form_dict.max_height)
			content = optimize_image(**args)

	kanivin.local.uploaded_file_url = file_url
	kanivin.local.uploaded_file = content
	kanivin.local.uploaded_filename = filename

	if content is not None and (kanivin.session.user == "Guest" or (user and not user.has_desk_access())):
		filetype = guess_type(filename)[0]
		if filetype not in ALLOWED_MIMETYPES:
			kanivin.throw(_("You can only upload JPG, PNG, PDF, TXT, CSV or Microsoft documents."))

	if method:
		method = kanivin.get_attr(method)
		is_whitelisted(method)
		return method()
	else:
		return kanivin.get_doc(
			{
				"doctype": "File",
				"attached_to_doctype": doctype,
				"attached_to_name": docname,
				"attached_to_field": fieldname,
				"folder": folder,
				"file_name": filename,
				"file_url": file_url,
				"is_private": cint(is_private),
				"content": content,
			}
		).save(ignore_permissions=ignore_permissions)


def check_write_permission(doctype: str | None = None, name: str | None = None):
	if not doctype:
		return

	if not name:
		kanivin.has_permission(doctype, "write", throw=True)
		return

	try:
		doc = kanivin.get_doc(doctype, name)
	except kanivin.DoesNotExistError:
		# doc has not been inserted yet, name is set to "new-some-doctype"
		# If doc inserts fine then only this attachment will be linked see file/utils.py:relink_mismatched_files
		kanivin.new_doc(doctype).check_permission("write")
		return

	doc.check_permission("write")


@kanivin.whitelist(allow_guest=True)
def download_file(file_url: str):
	"""
	Download file using token and REST API. Valid session or
	token is required to download private files.

	Method : GET
	Endpoints : download_file, kanivin.core.doctype.file.file.download_file
	URL Params : file_name = /path/to/file relative to site path
	"""
	file: "File" = kanivin.get_doc("File", {"file_url": file_url})
	if not file.is_downloadable():
		raise kanivin.PermissionError

	kanivin.local.response.filename = os.path.basename(file_url)
	kanivin.local.response.filecontent = file.get_content()
	kanivin.local.response.type = "download"


def get_attr(cmd):
	"""get method object from cmd"""
	if "." in cmd:
		method = kanivin.get_attr(cmd)
	else:
		deprecation_warning(
			f"Calling shorthand for {cmd} is deprecated, please specify full path in RPC call."
		)
		method = globals()[cmd]
	return method


def run_doc_method(method, docs=None, dt=None, dn=None, arg=None, args=None):
	"""run a whitelisted controller method"""
	from inspect import signature

	if not args and arg:
		args = arg

	if dt:  # not called from a doctype (from a page)
		if not dn:
			dn = dt  # single
		doc = kanivin.get_doc(dt, dn)

	else:
		docs = kanivin.parse_json(docs)
		doc = kanivin.get_doc(docs)
		doc._original_modified = doc.modified
		doc.check_if_latest()

	if not doc or not doc.has_permission("read"):
		throw_permission_error()

	try:
		args = kanivin.parse_json(args)
	except ValueError:
		pass

	method_obj = getattr(doc, method)
	fn = getattr(method_obj, "__func__", method_obj)
	is_whitelisted(fn)
	is_valid_http_method(fn)

	fnargs = list(signature(method_obj).parameters)

	if not fnargs or (len(fnargs) == 1 and fnargs[0] == "self"):
		response = doc.run_method(method)

	elif "args" in fnargs or not isinstance(args, dict):
		response = doc.run_method(method, args)

	else:
		response = doc.run_method(method, **args)

	kanivin.response.docs.append(doc)
	if response is None:
		return

	# build output as csv
	if cint(kanivin.form_dict.get("as_csv")):
		build_csv_response(response, _(doc.doctype).replace(" ", ""))
		return

	kanivin.response["message"] = response

	add_data_to_monitor(methodname=method)


# for backwards compatibility
runserverobj = run_doc_method
