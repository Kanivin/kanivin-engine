# Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import getpass

import kanivin
from kanivin.geo.doctype.country.country import import_country_and_currency
from kanivin.utils.password import update_password


def before_install():
	kanivin.reload_doc("core", "doctype", "doctype_state")
	kanivin.reload_doc("core", "doctype", "docfield")
	kanivin.reload_doc("core", "doctype", "docperm")
	kanivin.reload_doc("core", "doctype", "doctype_action")
	kanivin.reload_doc("core", "doctype", "doctype_link")
	kanivin.reload_doc("desk", "doctype", "form_tour_step")
	kanivin.reload_doc("desk", "doctype", "form_tour")
	kanivin.reload_doc("core", "doctype", "doctype")
	kanivin.clear_cache()


def after_install():
	create_user_type()
	install_basic_docs()

	from kanivin.core.doctype.file.utils import make_home_folder
	from kanivin.core.doctype.language.language import sync_languages

	make_home_folder()
	import_country_and_currency()
	sync_languages()

	# save default print setting
	print_settings = kanivin.get_doc("Print Settings")
	print_settings.save()

	# all roles to admin
	kanivin.get_doc("User", "Administrator").add_roles(*kanivin.get_all("Role", pluck="name"))

	# update admin password
	update_password("Administrator", get_admin_password())

	if not kanivin.conf.skip_setup_wizard:
		# only set home_page if the value doesn't exist in the db
		if not kanivin.db.get_default("desktop:home_page"):
			kanivin.db.set_default("desktop:home_page", "setup-wizard")
			kanivin.db.set_single_value("System Settings", "setup_complete", 0)

	# clear test log
	with open(kanivin.get_site_path(".test_log"), "w") as f:
		f.write("")

	add_standard_navbar_items()

	kanivin.db.commit()


def create_user_type():
	for user_type in ["System User", "Website User"]:
		if not kanivin.db.exists("User Type", user_type):
			kanivin.get_doc({"doctype": "User Type", "name": user_type, "is_standard": 1}).insert(
				ignore_permissions=True
			)


def install_basic_docs():
	# core users / roles
	install_docs = [
		{
			"doctype": "User",
			"name": "Administrator",
			"first_name": "Administrator",
			"email": "admin@example.com",
			"enabled": 1,
			"is_admin": 1,
			"roles": [{"role": "Administrator"}],
			"thread_notify": 0,
			"send_me_a_copy": 0,
		},
		{
			"doctype": "User",
			"name": "Guest",
			"first_name": "Guest",
			"email": "guest@example.com",
			"enabled": 1,
			"is_guest": 1,
			"roles": [{"role": "Guest"}],
			"thread_notify": 0,
			"send_me_a_copy": 0,
		},
		{"doctype": "Role", "role_name": "Report Manager"},
		{"doctype": "Role", "role_name": "Translator"},
		{
			"doctype": "Workflow State",
			"workflow_state_name": "Pending",
			"icon": "question-sign",
			"style": "",
		},
		{
			"doctype": "Workflow State",
			"workflow_state_name": "Approved",
			"icon": "ok-sign",
			"style": "Success",
		},
		{
			"doctype": "Workflow State",
			"workflow_state_name": "Rejected",
			"icon": "remove",
			"style": "Danger",
		},
		{"doctype": "Workflow Action Master", "workflow_action_name": "Approve"},
		{"doctype": "Workflow Action Master", "workflow_action_name": "Reject"},
		{"doctype": "Workflow Action Master", "workflow_action_name": "Review"},
		{
			"doctype": "Email Domain",
			"domain_name": "example.com",
			"email_id": "account@example.com",
			"password": "pass",
			"email_server": "imap.example.com",
			"use_imap": 1,
			"smtp_server": "smtp.example.com",
		},
		{
			"doctype": "Email Account",
			"domain": "example.com",
			"email_id": "notifications@example.com",
			"default_outgoing": 1,
		},
		{
			"doctype": "Email Account",
			"domain": "example.com",
			"email_id": "replies@example.com",
			"default_incoming": 1,
		},
	]

	for d in install_docs:
		try:
			kanivin.get_doc(d).insert(ignore_if_duplicate=True)
		except kanivin.NameError:
			pass


def get_admin_password():
	def ask_admin_password():
		admin_password = getpass.getpass("Set Administrator password: ")
		admin_password2 = getpass.getpass("Re-enter Administrator password: ")
		if not admin_password == admin_password2:
			print("\nPasswords do not match")
			return ask_admin_password()
		return admin_password

	admin_password = kanivin.conf.get("admin_password")
	if not admin_password:
		return ask_admin_password()
	return admin_password


def before_tests():
	if len(kanivin.get_installed_apps()) > 1:
		# don't run before tests if any other app is installed
		return

	kanivin.db.truncate("Custom Field")
	kanivin.db.truncate("Event")

	kanivin.clear_cache()

	# complete setup if missing
	if not int(kanivin.db.get_single_value("System Settings", "setup_complete") or 0):
		complete_setup_wizard()

	kanivin.db.set_single_value("Website Settings", "disable_signup", 0)
	kanivin.db.commit()
	kanivin.clear_cache()


def complete_setup_wizard():
	from kanivin.desk.page.setup_wizard.setup_wizard import setup_complete

	setup_complete(
		{
			"language": "English",
			"email": "test@erpnext.com",
			"full_name": "Test User",
			"password": "test",
			"country": "United States",
			"timezone": "America/New_York",
			"currency": "USD",
		}
	)


def add_standard_navbar_items():
	navbar_settings = kanivin.get_single("Navbar Settings")

	# don't add settings/help options if they're already present
	if navbar_settings.settings_dropdown and navbar_settings.help_dropdown:
		return

	navbar_settings.settings_dropdown = []
	navbar_settings.help_dropdown = []

	for item in kanivin.get_hooks("standard_navbar_items"):
		navbar_settings.append("settings_dropdown", item)

	for item in kanivin.get_hooks("standard_help_items"):
		navbar_settings.append("help_dropdown", item)

	navbar_settings.save()
