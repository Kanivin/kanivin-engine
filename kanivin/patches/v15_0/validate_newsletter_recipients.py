import kanivin
from kanivin.utils import validate_email_address


def execute():
	for name, email in kanivin.get_all("Email Group Member", fields=["name", "email"], as_list=True):
		if not validate_email_address(email, throw=False):
			kanivin.db.set_value("Email Group Member", name, "unsubscribed", 1)
			kanivin.db.commit()
