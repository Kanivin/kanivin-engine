# Copyright (c) 2021, Kanivin Pvt. Ltd. and Contributors
# MIT License. See license.txt


import functools

import kanivin


@kanivin.whitelist()
def get_google_fonts():
	return _get_google_fonts()


@functools.lru_cache
def _get_google_fonts():
	file_path = kanivin.get_app_path("kanivin", "data", "google_fonts.json")
	return kanivin.parse_json(kanivin.read_file(file_path))
