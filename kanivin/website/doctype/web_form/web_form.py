# Copyright (c) 2015, Kanivin Pvt. Ltd. and contributors
# License: MIT. See LICENSE

import json
import os

import kanivin
from kanivin import _, scrub
from kanivin.core.api.file import get_max_file_size
from kanivin.core.doctype.file.utils import remove_file_by_url
from kanivin.desk.form.meta import get_code_files_via_hooks
from kanivin.modules.utils import export_module_json, get_doc_module
from kanivin.permissions import check_doctype_permission
from kanivin.rate_limiter import rate_limit
from kanivin.utils import dict_with_keys, strip_html
from kanivin.utils.caching import redis_cache
from kanivin.website.utils import get_boot_data, get_comment_list, get_sidebar_items
from kanivin.website.website_generator import WebsiteGenerator


class WebForm(WebsiteGenerator):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from kanivin.types import DF
		from kanivin.website.doctype.web_form_field.web_form_field import WebFormField
		from kanivin.website.doctype.web_form_list_column.web_form_list_column import WebFormListColumn

		allow_comments: DF.Check
		allow_delete: DF.Check
		allow_edit: DF.Check
		allow_incomplete: DF.Check
		allow_multiple: DF.Check
		allow_print: DF.Check
		allowed_embedding_domains: DF.SmallText | None
		anonymous: DF.Check
		apply_document_permissions: DF.Check
		banner_image: DF.AttachImage | None
		breadcrumbs: DF.Code | None
		button_label: DF.Data | None
		client_script: DF.Code | None
		condition: DF.Code | None
		custom_css: DF.Code | None
		doc_type: DF.Link
		introduction_text: DF.TextEditor | None
		is_standard: DF.Check
		list_columns: DF.Table[WebFormListColumn]
		list_title: DF.Data | None
		login_required: DF.Check
		max_attachment_size: DF.Int
		meta_description: DF.SmallText | None
		meta_image: DF.AttachImage | None
		meta_title: DF.Data | None
		module: DF.Link | None
		print_format: DF.Link | None
		published: DF.Check
		route: DF.Data | None
		show_attachments: DF.Check
		show_list: DF.Check
		show_sidebar: DF.Check
		success_message: DF.Text | None
		success_title: DF.Data | None
		success_url: DF.Data | None
		title: DF.Data
		web_form_fields: DF.Table[WebFormField]
		website_sidebar: DF.Link | None
	# end: auto-generated types
	website = kanivin._dict(no_cache=1)

	def validate(self):
		super().validate()

		if not self.module:
			self.module = kanivin.db.get_value("DocType", self.doc_type, "module")

		in_user_env = not (
			kanivin.flags.in_install
			or kanivin.flags.in_patch
			or kanivin.flags.in_test
			or kanivin.flags.in_fixtures
		)
		if in_user_env and self.is_standard and not kanivin.conf.developer_mode:
			# only published can be changed for standard web forms
			if self.has_value_changed("published"):
				published_value = self.published
				self.reload()
				self.published = published_value
			else:
				kanivin.throw(_("You need to be in developer mode to edit a Standard Web Form"))

		if not kanivin.flags.in_import:
			self.validate_fields()

	def validate_fields(self):
		"""Validate all fields are present"""
		from kanivin.model import no_value_fields

		meta = kanivin.get_meta(self.doc_type)
		missing = [
			df.fieldname
			for df in self.web_form_fields
			if df.fieldname and (df.fieldtype not in no_value_fields and not meta.has_field(df.fieldname))
		]

		if missing:
			kanivin.throw(_("Following fields are missing:") + "<br>" + "<br>".join(missing))

	def reset_field_parent(self):
		"""Convert link fields to select with names as options"""
		for df in self.web_form_fields:
			df.parent = self.doc_type

	# export
	def on_update(self):
		"""
		Writes the .txt for this page and if write_content is checked,
		it will write out a .html file
		"""
		path = export_module_json(self, self.is_standard, self.module)

		if path:
			# js
			if not os.path.exists(path + ".js"):
				with open(path + ".js", "w") as f:
					f.write(
						"""kanivin.ready(function() {
	// bind events here
})"""
					)

			# py
			if not os.path.exists(path + ".py"):
				with open(path + ".py", "w") as f:
					f.write(
						"""import kanivin

def get_context(context):
	# do your magic here
	pass
"""
					)

	def get_context(self, context):
		"""Build context to render the `web_form.html` template"""
		context.in_edit_mode = False
		context.in_view_mode = False

		if kanivin.form_dict.is_list:
			context.template = "website/doctype/web_form/templates/web_list.html"
		else:
			context.template = "website/doctype/web_form/templates/web_form.html"

		# check permissions
		if kanivin.form_dict.name:
			assert isinstance(kanivin.form_dict.name, str | int)

			if kanivin.session.user == "Guest":
				kanivin.throw(
					_("You need to be logged in to access this {0}.").format(self.doc_type),
					kanivin.PermissionError,
				)

			if not kanivin.db.exists(self.doc_type, kanivin.form_dict.name):
				check_doctype_permission(self.doc_type)
				raise kanivin.PageDoesNotExistError()

			if not self.has_web_form_permission(self.doc_type, kanivin.form_dict.name):
				check_doctype_permission(self.doc_type)
				kanivin.throw(
					_("You don't have the permissions to access this document"), kanivin.PermissionError
				)

		if kanivin.local.path == self.route:
			path = f"/{self.route}/list" if self.show_list else f"/{self.route}/new"
			kanivin.redirect(path)

		if kanivin.form_dict.is_list and not self.show_list:
			kanivin.redirect(f"/{self.route}/new")

		if kanivin.form_dict.is_edit and not self.allow_edit:
			context.in_view_mode = True
			kanivin.redirect(f"/{self.route}/{kanivin.form_dict.name}")

		if kanivin.form_dict.is_edit:
			context.in_edit_mode = True

		if kanivin.form_dict.is_read:
			context.in_view_mode = True

		if (
			not kanivin.form_dict.is_edit
			and not kanivin.form_dict.is_read
			and self.allow_edit
			and kanivin.form_dict.name
		):
			context.in_edit_mode = True
			kanivin.redirect(f"/{kanivin.local.path}/edit")

		if (
			kanivin.session.user != "Guest"
			and self.login_required
			and not self.allow_multiple
			and not kanivin.form_dict.name
			and not kanivin.form_dict.is_list
		):
			condition_json = json.loads(self.condition_json) if self.condition_json else []
			condition_json.append(["owner", "=", kanivin.session.user])
			names = kanivin.get_all(self.doc_type, filters=condition_json, pluck="name")
			if names:
				context.in_view_mode = True
				kanivin.redirect(f"/{self.route}/{names[0]}")

		# Show new form when
		# - User is Guest
		# - Login not required
		route_to_new = kanivin.session.user == "Guest" or not self.login_required
		if not kanivin.form_dict.is_new and route_to_new:
			kanivin.redirect(f"/{self.route}/new")

		self.reset_field_parent()

		# add keys from form_dict to context
		context.update(dict_with_keys(kanivin.form_dict, ["is_list", "is_new", "is_edit", "is_read"]))

		for df in self.web_form_fields:
			if df.fieldtype == "Column Break":
				context.has_column_break = True
				break

		# load web form doc
		context.web_form_doc = self.as_dict(no_nulls=True)
		context.web_form_doc.update(
			dict_with_keys(context, ["is_list", "is_new", "in_edit_mode", "in_view_mode"])
		)

		if self.show_sidebar and self.website_sidebar:
			context.sidebar_items = get_sidebar_items(self.website_sidebar)

		if kanivin.form_dict.is_list:
			self.load_list_data(context)
		else:
			self.load_form_data(context)

		self.add_custom_context_and_script(context)
		self.load_translations(context)
		self.add_metatags(context)

		context.boot = get_boot_data()
		context.boot["link_title_doctypes"] = kanivin.boot.get_link_title_doctypes()

		context.webform_banner_image = self.banner_image
		context.pop("banner_image", None)

	def add_metatags(self, context):
		description = self.meta_description

		if not description and self.introduction_text:
			description = self.introduction_text[:140]

		context.metatags = {
			"title": self.meta_title or self.title,
			"description": description,
			"image": self.meta_image,
		}

	def load_translations(self, context):
		messages = [
			"Sr",
			"Attach",
			"Next",
			"Previous",
			"Discard?",
			"Cancel",
			"Discard:Button in web form",
			"Edit:Button in web form",
			"See previous responses:Button in web form",
			"Edit your response:Button in web form",
			"Are you sure you want to discard the changes?",
			"Mandatory fields required::Error message in web form",
			"Invalid values for fields::Error message in web form",
			"Error:Title of error message in web form",
			"Page {0} of {1}",
			"Couldn't save, please check the data you have entered",
			"Validation Error",
			self.title,
			self.introduction_text,
			self.success_title,
			self.success_message,
			self.list_title,
			self.button_label,
			self.meta_title,
			self.meta_description,
		]

		for field in self.web_form_fields:
			messages.extend([field.label, field.description])
			if field.fieldtype == "Select" and field.options:
				messages.extend(field.options.split("\n"))

		# When at least one field in self.web_form_fields has fieldtype "Table" then add "No data" to messages
		if any(field.fieldtype == "Table" for field in self.web_form_fields):
			messages.append("Move")
			messages.append("Insert Above")
			messages.append("Insert Below")
			messages.append("Duplicate")
			messages.append("Shortcuts")
			messages.append("Ctrl + Up")
			messages.append("Ctrl + Down")
			messages.append("ESC")
			messages.append("Editing Row")
			messages.append("Add / Remove Columns")
			messages.append("Fieldname")
			messages.append("Column Width")
			messages.append("Configure Columns")
			messages.append("Select Fields")
			messages.append("Select All")
			messages.append("Update")
			messages.append("Reset to default")
			messages.append("No Data")
			messages.append("Delete")
			messages.append("Delete All")
			messages.append("Add Row")
			messages.append("Add Multiple")
			messages.append("Download")
			messages.append("of")
			messages.append("Upload")
			messages.append("Last")
			messages.append("First")
			messages.append("No.:Title of the 'row number' column")

		# Phone Picker
		if any(field.fieldtype == "Phone" for field in self.web_form_fields):
			messages.append("Search for countries...")

		# Dates
		if any(field.fieldtype == "Date" for field in self.web_form_fields):
			messages.append("Now")
			messages.append("Today")
			messages.append("Date {0} must be in format: {1}")
			messages.append("{0} to {1}")

		# Time
		if any(field.fieldtype == "Time" for field in self.web_form_fields):
			messages.append("Now")

		messages.extend(col.get("label") if col else "" for col in self.list_columns)

		context.translated_messages = kanivin.as_json({message: _(message) for message in messages if message})

	def load_list_data(self, context):
		if not self.list_columns:
			self.list_columns = get_in_list_view_fields(self.doc_type)
			context.web_form_doc.list_columns = self.list_columns

	def load_form_data(self, context):
		"""Load document `doc` and `layout` properties for template"""
		context.parents = []
		if self.show_list:
			context.parents.append(
				{
					"label": _(self.title),
					"route": f"{self.route}/list",
				}
			)

		context.parents = self.get_parents(context)

		if self.breadcrumbs:
			context.parents = kanivin.safe_eval(self.breadcrumbs, {"_": _})

		if self.show_list and kanivin.form_dict.is_new:
			context.title = _("New {0}").format(context.title)

		context.has_header = (kanivin.form_dict.name or kanivin.form_dict.is_new) and (
			kanivin.session.user != "Guest" or not self.login_required
		)

		if context.success_message:
			context.success_message = kanivin.db.escape(context.success_message.replace("\n", "<br>")).strip(
				"'"
			)

		if not context.max_attachment_size:
			context.max_attachment_size = get_max_file_size() / 1024 / 1024

		# For Table fields, server-side processing for meta
		for field in context.web_form_doc.web_form_fields:
			if field.fieldtype == "Table":
				field.fields = get_in_list_view_fields(field.options)

			if field.fieldtype == "Link":
				field.fieldtype = "Autocomplete"
				field.options = get_link_options(
					self.name, field.options, field.allow_read_on_all_link_options
				)

		context.reference_doc = {}

		# load reference doc
		if kanivin.form_dict.name:
			context.doc_name = kanivin.form_dict.name
			context.reference_doc = kanivin.get_doc(self.doc_type, context.doc_name)
			context.web_form_title = context.title
			context.title = (
				strip_html(context.reference_doc.get(context.reference_doc.meta.get_title_field()))
				or context.doc_name
			)
			context.reference_doc.add_seen()
			context.reference_doctype = context.reference_doc.doctype
			context.reference_name = context.reference_doc.name

			if self.show_attachments:
				context.attachments = kanivin.get_all(
					"File",
					filters={
						"attached_to_name": context.reference_name,
						"attached_to_doctype": context.reference_doctype,
						"is_private": 0,
					},
					fields=["file_name", "file_url", "file_size"],
				)

			if self.allow_comments:
				context.comment_list = get_comment_list(
					context.reference_doc.doctype, context.reference_doc.name
				)

			context.reference_doc = context.reference_doc.as_dict(no_nulls=True)

	def add_custom_context_and_script(self, context):
		"""Update context from module if standard and append script"""
		if self.is_standard:
			web_form_module = get_web_form_module(self)
			new_context = web_form_module.get_context(context)

			if new_context:
				context.update(new_context)

			js_path = os.path.join(os.path.dirname(web_form_module.__file__), scrub(self.name) + ".js")
			if os.path.exists(js_path):
				script = kanivin.render_template(open(js_path).read(), context)

				for path in get_code_files_via_hooks("webform_include_js", context.doc_type):
					custom_js = kanivin.render_template(open(path).read(), context)
					script = "\n\n".join([script, custom_js])

				context.script = script

			css_path = os.path.join(os.path.dirname(web_form_module.__file__), scrub(self.name) + ".css")
			if os.path.exists(css_path):
				style = open(css_path).read()

				for path in get_code_files_via_hooks("webform_include_css", context.doc_type):
					custom_css = open(path).read()
					style = "\n\n".join([style, custom_css])

				context.style = style

	def get_parents(self, context):
		parents = None

		if context.is_list and not context.parents:
			parents = [{"title": _("My Account"), "name": "me"}]
		elif context.parents:
			parents = context.parents

		return parents

	def validate_mandatory(self, doc):
		"""Validate mandatory web form fields"""
		missing = [f for f in self.web_form_fields if f.reqd and doc.get(f.fieldname) in (None, [], "")]
		if missing:
			kanivin.throw(
				_("Mandatory Information missing:")
				+ "<br><br>"
				+ "<br>".join(f"{d.label} ({d.fieldtype})" for d in missing)
			)

	def allow_website_search_indexing(self):
		return False

	def has_web_form_permission(self, doctype, name, ptype="read"):
		if kanivin.session.user == "Guest":
			return False

		if self.apply_document_permissions:
			return kanivin.get_doc(doctype, name).has_permission(permtype=ptype)

		# owner matches
		elif kanivin.db.get_value(doctype, name, "owner") == kanivin.session.user:
			return True

		elif kanivin.has_website_permission(name, ptype=ptype, doctype=doctype):
			return True

		elif check_webform_perm(doctype, name):
			return True

		else:
			return False


def get_web_form_module(doc):
	if doc.is_standard:
		return get_doc_module(doc.module, doc.doctype, doc.name)


@kanivin.whitelist(allow_guest=True)
@rate_limit(key="web_form", limit=10, seconds=60)
def accept(web_form, data):
	"""Save the web form"""
	data = kanivin._dict(json.loads(data))

	files = []
	files_to_delete = []

	web_form = kanivin.get_doc("Web Form", web_form)
	doctype = web_form.doc_type
	user = kanivin.session.user

	if web_form.anonymous and kanivin.session.user != "Guest":
		kanivin.session.user = "Guest"

	if data.name and not web_form.allow_edit:
		kanivin.throw(_("You are not allowed to update this Web Form Document"))

	kanivin.flags.in_web_form = True
	meta = kanivin.get_meta(doctype)

	if data.name:
		# update
		doc = kanivin.get_doc(doctype, data.name)
	else:
		# insert
		doc = kanivin.new_doc(doctype)

	# set values
	for field in web_form.web_form_fields:
		fieldname = field.fieldname
		df = meta.get_field(fieldname)
		value = data.get(fieldname, "")

		if df and df.fieldtype in ("Attach", "Attach Image"):
			if value and "data:" and "base64" in value:
				files.append((fieldname, value))
				if not doc.name:
					doc.set(fieldname, "")
				continue

			elif not value and doc.get(fieldname):
				files_to_delete.append(doc.get(fieldname))

		doc.set(fieldname, value)

	if doc.name:
		if web_form.has_web_form_permission(doctype, doc.name, "write"):
			doc.save(ignore_permissions=True)
		else:
			# only if permissions are present
			doc.save()

	else:
		# insert
		if web_form.login_required and kanivin.session.user == "Guest":
			kanivin.throw(_("You must login to submit this form"))

		ignore_mandatory = True if files else False

		doc.insert(ignore_permissions=True, ignore_mandatory=ignore_mandatory)

	# add files
	if files:
		for f in files:
			fieldname, filedata = f

			# remove earlier attached file (if exists)
			if doc.get(fieldname):
				remove_file_by_url(doc.get(fieldname), doctype=doctype, name=doc.name)

			# save new file
			filename, dataurl = filedata.split(",", 1)
			_file = kanivin.get_doc(
				{
					"doctype": "File",
					"file_name": filename,
					"attached_to_doctype": doctype,
					"attached_to_name": doc.name,
					"content": dataurl,
					"decode": True,
				}
			)
			_file.save()

			# update values
			doc.set(fieldname, _file.file_url)

		doc.save(ignore_permissions=True)

	if files_to_delete:
		for f in files_to_delete:
			if f:
				remove_file_by_url(f, doctype=doctype, name=doc.name)

	if web_form.anonymous and kanivin.session.user == "Guest" and user:
		kanivin.session.user = user

	kanivin.flags.web_form_doc = doc
	return doc


@kanivin.whitelist()
def delete(web_form_name: str, docname: str | int):
	web_form = kanivin.get_doc("Web Form", web_form_name)

	owner = kanivin.db.get_value(web_form.doc_type, docname, "owner")
	if kanivin.session.user == owner and web_form.allow_delete:
		kanivin.delete_doc(web_form.doc_type, docname, ignore_permissions=True)
	else:
		raise kanivin.PermissionError("Not Allowed")


@kanivin.whitelist()
def delete_multiple(web_form_name: str, docnames):
	web_form = kanivin.get_doc("Web Form", web_form_name)

	docnames = json.loads(docnames)

	allowed_docnames = []
	restricted_docnames = []

	for docname in docnames:
		assert isinstance(docname, str | int)

		owner = kanivin.db.get_value(web_form.doc_type, docname, "owner")
		if kanivin.session.user == owner and web_form.allow_delete:
			allowed_docnames.append(docname)
		else:
			restricted_docnames.append(docname)

	for docname in allowed_docnames:
		kanivin.delete_doc(web_form.doc_type, docname, ignore_permissions=True)

	if restricted_docnames:
		raise kanivin.PermissionError(
			"You do not have permisssion to delete " + ", ".join(restricted_docnames)
		)


def check_webform_perm(doctype, name):
	doc = kanivin.get_doc(doctype, name)
	if hasattr(doc, "has_webform_permission"):
		if doc.has_webform_permission():
			return True


@kanivin.whitelist(allow_guest=True)
def get_web_form_filters(web_form_name):
	web_form = kanivin.get_doc("Web Form", web_form_name)
	return [field for field in web_form.web_form_fields if field.show_in_filter]


@kanivin.whitelist(allow_guest=True)
def get_form_data(doctype, docname=None, web_form_name=None):
	web_form = kanivin.get_doc("Web Form", web_form_name)

	if web_form.login_required and kanivin.session.user == "Guest":
		kanivin.throw(_("Not Permitted"), kanivin.PermissionError)

	out = kanivin._dict()
	out.web_form = web_form

	if kanivin.session.user != "Guest" and not docname and not web_form.allow_multiple:
		docname = kanivin.db.get_value(doctype, {"owner": kanivin.session.user}, "name")

	if docname:
		doc = kanivin.get_doc(doctype, docname)
		if web_form.has_web_form_permission(doctype, docname, ptype="read"):
			out.doc = doc
		else:
			kanivin.throw(_("Not permitted"), kanivin.PermissionError)

	# For Table fields, server-side processing for meta
	for field in out.web_form.web_form_fields:
		if field.fieldtype == "Table":
			field.fields = get_in_list_view_fields(field.options)
			out.update({field.fieldname: field.fields})

		if field.fieldtype == "Link":
			field.fieldtype = "Autocomplete"
			field.options = get_link_options(
				web_form_name, field.options, field.allow_read_on_all_link_options
			)

	return out


@kanivin.whitelist()
def get_in_list_view_fields(doctype):
	meta = kanivin.get_meta(doctype)
	fields = []

	if meta.title_field:
		fields.append(meta.title_field)
	else:
		fields.append("name")

	if meta.has_field("status"):
		fields.append("status")

	fields += [df.fieldname for df in meta.fields if df.in_list_view and df.fieldname not in fields]

	def get_field_df(fieldname):
		if fieldname == "name":
			return {"label": "Name", "fieldname": "name", "fieldtype": "Data"}
		return meta.get_field(fieldname).as_dict()

	return [get_field_df(f) for f in fields]


def get_link_options(web_form_name, doctype, allow_read_on_all_link_options=False):
	web_form: WebForm = kanivin.get_doc("Web Form", web_form_name)

	if web_form.login_required and kanivin.session.user == "Guest":
		kanivin.throw(_("You must be logged in to use this form."), kanivin.PermissionError)

	if not web_form.published or not any(f for f in web_form.web_form_fields if f.options == doctype):
		kanivin.throw(
			_("You don't have permission to access the {0} DocType.").format(doctype), kanivin.PermissionError
		)

	link_options, filters = [], {}
	if web_form.login_required and not allow_read_on_all_link_options:
		filters = {"owner": kanivin.session.user}

	fields = ["name as value"]

	meta = kanivin.get_meta(doctype)
	show_title_field = meta.title_field and meta.show_title_field_in_link

	if show_title_field:
		fields.append(f"{meta.title_field} as label")

	link_options = kanivin.get_all(doctype, filters, fields)

	if show_title_field:
		if meta.translated_doctype:
			# Translate the labels if "Translate Link Fields" is enabled
			link_options = [{"value": row.value, "label": _(row.label)} for row in link_options]

		return json.dumps(link_options, default=str)
	else:
		if meta.translated_doctype:
			# Add `label` as the translated name if "Translate Link Fields" is enabled
			return [{"value": row.value, "label": _(row.value)} for row in link_options]

		# Use the actual names as options without labels
		return "\n".join([str(doc.value) for doc in link_options])


@redis_cache(ttl=60 * 60)
def get_published_web_forms() -> dict[str, str]:
	return kanivin.get_all("Web Form", ["name", "route", "modified"], {"published": 1})
