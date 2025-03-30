import kanivin
from kanivin.desk.utils import slug


def execute():
	for doctype in kanivin.get_all("DocType", ["name", "route"], dict(istable=0)):
		if not doctype.route:
			kanivin.db.set_value("DocType", doctype.name, "route", slug(doctype.name), update_modified=False)
