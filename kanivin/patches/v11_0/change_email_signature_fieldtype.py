# Copyright (c) 2018, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import kanivin


def execute():
	signatures = kanivin.db.get_list("User", {"email_signature": ["!=", ""]}, ["name", "email_signature"])
	kanivin.reload_doc("core", "doctype", "user")
	for d in signatures:
		signature = d.get("email_signature")
		signature = signature.replace("\n", "<br>")
		signature = "<div>" + signature + "</div>"
		kanivin.db.set_value("User", d.get("name"), "email_signature", signature)
