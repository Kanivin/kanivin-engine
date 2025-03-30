import kanivin


def execute():
	singles = kanivin.qb.Table("tabSingles")
	kanivin.qb.from_(singles).delete().where(
		(singles.doctype == "System Settings") & (singles.field == "is_first_startup")
	).run()
