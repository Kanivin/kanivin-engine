import kanivin


def execute():
	if kanivin.db.db_type == "mariadb":
		kanivin.db.sql_ddl("alter table `tabSingles` modify column `value` longtext")
