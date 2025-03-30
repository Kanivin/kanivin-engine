import kanivin


def execute():
	kanivin.db.delete("DocType", {"name": "Feedback Request"})
