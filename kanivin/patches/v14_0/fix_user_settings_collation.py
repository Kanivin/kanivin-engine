import kanivin


def execute():
	if kanivin.db.db_type == "mariadb":
		kanivin.db.sql(
			"ALTER TABLE __UserSettings CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
		)
