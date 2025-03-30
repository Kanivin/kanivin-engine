import kanivin


def execute():
	kanivin.db.change_column_type("__Auth", column="password", type="TEXT")
