import kanivin


def execute():
	table = kanivin.qb.DocType("Report")
	kanivin.qb.update(table).set(table.prepared_report, 0).where(table.disable_prepared_report == 1)
