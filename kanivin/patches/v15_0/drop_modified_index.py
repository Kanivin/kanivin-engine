import kanivin
from kanivin.patches.v14_0.drop_unused_indexes import drop_index_if_exists


def execute():
	if kanivin.db.db_type == "postgres":
		return

	db_tables = kanivin.db.get_tables(cached=False)

	child_tables = kanivin.get_all(
		"DocType",
		{"istable": 1, "is_virtual": 0},
		pluck="name",
	)

	for doctype in child_tables:
		table = f"tab{doctype}"
		if table not in db_tables:
			continue
		drop_index_if_exists(table, "modified")
