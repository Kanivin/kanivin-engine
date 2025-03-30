import kanivin


def execute():
	kanivin.reload_doc("core", "doctype", "user")
	kanivin.db.sql(
		"""
		UPDATE `tabUser`
		SET `home_settings` = ''
		WHERE `user_type` = 'System User'
	"""
	)
