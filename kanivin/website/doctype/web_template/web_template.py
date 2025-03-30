# Copyright (c) 2020, Kanivin and contributors
# License: MIT. See LICENSE

import os
from shutil import rmtree

import kanivin
from kanivin import _
from kanivin.model.document import Document
from kanivin.modules.export_file import get_module_path, scrub_dt_dn, write_document_file
from kanivin.website.utils import clear_cache


class WebTemplate(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from kanivin.types import DF
		from kanivin.website.doctype.web_template_field.web_template_field import WebTemplateField

		fields: DF.Table[WebTemplateField]
		module: DF.Link | None
		standard: DF.Check
		template: DF.Code | None
		type: DF.Literal["Component", "Section", "Navbar", "Footer"]

	# end: auto-generated types

	def validate(self):
		if self.standard and not (kanivin.conf.developer_mode or kanivin.flags.in_patch):
			kanivin.throw(_("Enable developer mode to create a standard Web Template"))

		for field in self.fields:
			if not field.fieldname:
				field.fieldname = kanivin.scrub(field.label)

	def before_save(self):
		if kanivin.conf.developer_mode:
			# custom to standard
			if self.standard:
				self.export_to_files()

			# standard to custom
			was_standard = (self.get_doc_before_save() or {}).get("standard")
			if was_standard and not self.standard:
				self.import_from_files()

	def on_update(self):
		"""Clear cache for all Web Pages in which this template is used"""
		routes = kanivin.get_all(
			"Web Page",
			filters=[
				["Web Page Block", "web_template", "=", self.name],
				["Web Page", "published", "=", 1],
			],
			pluck="route",
		)
		for route in routes:
			clear_cache(route)

	def on_trash(self):
		if kanivin.conf.developer_mode and self.standard:
			# delete template html and json files
			rmtree(self.get_template_folder())

	def export_to_files(self):
		"""Export Web Template to a new folder.

		Doc is exported as JSON. The content of the `template` field gets
		written into a separate HTML file. The template should not be contained
		in the JSON.
		"""
		html, self.template = self.template, ""
		write_document_file(self, create_init=True)
		self.create_template_file(html)

	def import_from_files(self):
		self.template = self.get_template(standard=True)
		rmtree(self.get_template_folder())

	def create_template_file(self, html=None):
		"""Touch a HTML file for the Web Template and add existing content, if any."""
		if self.standard:
			path = self.get_template_path()
			if not os.path.exists(path):
				with open(path, "w") as template_file:
					if html:
						template_file.write(html)

	def get_template_folder(self):
		"""Return the absolute path to the template's folder."""
		module = self.module or "Website"
		module_path = get_module_path(module)
		doctype, docname = scrub_dt_dn(self.doctype, self.name)

		return os.path.join(module_path, doctype, docname)

	def get_template_path(self):
		"""Return the absolute path to the template's HTML file."""
		folder = self.get_template_folder()
		file_name = kanivin.scrub(self.name) + ".html"

		return os.path.join(folder, file_name)

	def get_template(self, standard=False):
		"""Get the jinja template string.

		Params:
		standard - if True, look on the disk instead of in the database.
		"""
		if standard:
			template = self.get_template_path()
			with open(template) as template_file:
				template = template_file.read()
		else:
			template = self.template

		return template

	def render(self, values=None):
		if not values:
			values = {}
		values = kanivin.parse_json(values)
		values.update({"values": values})
		template = self.get_template(self.standard)

		return kanivin.render_template(template, values)
