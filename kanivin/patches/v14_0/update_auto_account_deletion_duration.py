import kanivin


def execute():
	days = kanivin.db.get_single_value("Website Settings", "auto_account_deletion")
	kanivin.db.set_single_value("Website Settings", "auto_account_deletion", days * 24)
