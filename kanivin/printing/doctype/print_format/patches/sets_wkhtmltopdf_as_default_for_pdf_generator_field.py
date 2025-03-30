import kanivin


def execute():
	"""sets "wkhtmltopdf" as default for pdf_generator field"""
	for pf in kanivin.get_all("Print Format", pluck="name"):
		kanivin.db.set_value("Print Format", pf, "pdf_generator", "wkhtmltopdf", update_modified=False)
