# Copyright (c) 2021, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

from click import secho

import kanivin


def execute():
	if kanivin.get_hooks("jenv"):
		print()
		secho(
			'WARNING: The hook "jenv" is deprecated. Follow the migration guide to use the new "jinja" hook.',
			fg="yellow",
		)
		secho("https://github.com/kanivin/kanivin/wiki/Migrating-to-Version-13", fg="yellow")
		print()
