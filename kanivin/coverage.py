# Copyright (c) 2021, Kanivin Pvt. Ltd. and Contributors
# MIT License. See LICENSE
"""
	kanivin.coverage
	~~~~~~~~~~~~~~~~

	Coverage settings for kanivin
"""

STANDARD_INCLUSIONS = ["*.py"]

STANDARD_EXCLUSIONS = [
	"*.js",
	"*.xml",
	"*.pyc",
	"*.css",
	"*.less",
	"*.scss",
	"*.vue",
	"*.html",
	"*/test_*",
	"*/node_modules/*",
	"*/doctype/*/*_dashboard.py",
	"*/patches/*",
]

# tested via commands' test suite
TESTED_VIA_CLI = [
	"*/kanivin/installer.py",
	"*/kanivin/build.py",
	"*/kanivin/database/__init__.py",
	"*/kanivin/database/db_manager.py",
	"*/kanivin/database/**/setup_db.py",
]

FRAPPE_EXCLUSIONS = [
	"*/tests/*",
	"*/commands/*",
	"*/kanivin/change_log/*",
	"*/kanivin/exceptions*",
	"*/kanivin/coverage.py",
	"*kanivin/setup.py",
	"*/doctype/*/*_dashboard.py",
	"*/patches/*",
	*TESTED_VIA_CLI,
]


class CodeCoverage:
	def __init__(self, with_coverage, app):
		self.with_coverage = with_coverage
		self.app = app or "kanivin"

	def __enter__(self):
		if self.with_coverage:
			import os

			from coverage import Coverage

			from kanivin.utils import get_bench_path

			# Generate coverage report only for app that is being tested
			source_path = os.path.join(get_bench_path(), "apps", self.app)
			omit = STANDARD_EXCLUSIONS[:]

			if self.app == "kanivin":
				omit.extend(FRAPPE_EXCLUSIONS)

			self.coverage = Coverage(source=[source_path], omit=omit, include=STANDARD_INCLUSIONS)
			self.coverage.start()

	def __exit__(self, exc_type, exc_value, traceback):
		if self.with_coverage:
			self.coverage.stop()
			self.coverage.save()
			self.coverage.xml_report()
			print("Saved Coverage")
