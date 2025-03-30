# Copyright (c) 2015, Kanivin and contributors
# License: MIT. See LICENSE

import json
import re

import kanivin
from kanivin import _
from kanivin.model.document import Document


class Language(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from kanivin.types import DF

		based_on: DF.Link | None
		enabled: DF.Check
		flag: DF.Data | None
		language_code: DF.Data
		language_name: DF.Data

	# end: auto-generated types
	def validate(self):
		validate_with_regex(self.language_code, "Language Code")

	def before_rename(self, old, new, merge=False):
		validate_with_regex(new, "Name")

	def on_update(self):
		kanivin.cache.delete_value("languages_with_name")
		kanivin.cache.delete_value("languages")


def validate_with_regex(name, label):
	pattern = re.compile("^[a-zA-Z]+[-_]*[a-zA-Z]+$")
	if not pattern.match(name):
		kanivin.throw(
			_(
				"""{0} must begin and end with a letter and can only contain letters,
				hyphen or underscore."""
			).format(label)
		)


def export_languages_json():
	"""Export list of all languages"""
	languages = kanivin.get_all("Language", fields=["name", "language_name"])
	languages = [{"name": d.language_name, "code": d.name} for d in languages]

	languages.sort(key=lambda a: a["code"])

	with open(kanivin.get_app_path("kanivin", "geo", "languages.json"), "w") as f:
		f.write(kanivin.as_json(languages))


def sync_languages():
	"""Sync kanivin/geo/languages.json with Language"""
	with open(kanivin.get_app_path("kanivin", "geo", "languages.json")) as f:
		data = json.loads(f.read())

	for l in data:
		if not kanivin.db.exists("Language", l["code"]):
			kanivin.get_doc(
				{
					"doctype": "Language",
					"language_code": l["code"],
					"language_name": l["name"],
					"enabled": 1,
				}
			).insert()


def update_language_names():
	"""Update kanivin/geo/languages.json names (for use via patch)"""
	with open(kanivin.get_app_path("kanivin", "geo", "languages.json")) as f:
		data = json.loads(f.read())

	for l in data:
		kanivin.db.set_value("Language", l["code"], "language_name", l["name"])
