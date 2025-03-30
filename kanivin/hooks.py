import os

from . import __version__ as app_version

app_name = "kanivin"
app_title = "Kanivin Framework"
app_publisher = "Kanivin"
app_description = "Full stack web framework with Python, Javascript, MariaDB, Redis, Node"
app_license = "MIT"
app_logo_url = "/assets/kanivin/images/kanivin-framework-logo.svg"
develop_version = "15.x.x-develop"

app_email = "developers@kanivin.io"

before_install = "kanivin.utils.install.before_install"
after_install = "kanivin.utils.install.after_install"

page_js = {"setup-wizard": "public/js/kanivin/setup_wizard.js"}

# website
app_include_js = [
	"libs.bundle.js",
	"desk.bundle.js",
	"list.bundle.js",
	"form.bundle.js",
	"controls.bundle.js",
	"report.bundle.js",
	"telemetry.bundle.js",
	"billing.bundle.js",
]

app_include_css = [
	"desk.bundle.css",
	"report.bundle.css",
]
app_include_icons = [
	"kanivin/icons/timeless/icons.svg",
	"kanivin/icons/espresso/icons.svg",
]

doctype_js = {
	"Web Page": "public/js/kanivin/utils/web_template.js",
	"Website Settings": "public/js/kanivin/utils/web_template.js",
}

web_include_js = ["website_script.js"]

web_include_css = []

email_css = ["email.bundle.css"]

website_route_rules = [
	{"from_route": "/blog/<category>", "to_route": "Blog Post"},
	{"from_route": "/kb/<category>", "to_route": "Help Article"},
	{"from_route": "/newsletters", "to_route": "Newsletter"},
	{"from_route": "/profile", "to_route": "me"},
	{"from_route": "/app/<path:app_path>", "to_route": "app"},
]

website_redirects = [
	{"source": r"/desk(.*)", "target": r"/app\1"},
	{
		"source": "/.well-known/openid-configuration",
		"target": "/api/method/kanivin.integrations.oauth2.openid_configuration",
	},
]

base_template = "templates/base.html"

write_file_keys = ["file_url", "file_name"]

notification_config = "kanivin.core.notifications.get_notification_config"

before_tests = "kanivin.utils.install.before_tests"

email_append_to = ["Event", "ToDo", "Communication"]

calendars = ["Event"]

leaderboards = "kanivin.desk.leaderboard.get_leaderboards"

# login

on_session_creation = [
	"kanivin.core.doctype.activity_log.feed.login_feed",
	"kanivin.core.doctype.user.user.notify_admin_access_to_system_manager",
]

on_logout = "kanivin.core.doctype.session_default_settings.session_default_settings.clear_session_defaults"

# PDF
pdf_header_html = "kanivin.utils.pdf.pdf_header_html"
pdf_body_html = "kanivin.utils.pdf.pdf_body_html"
pdf_footer_html = "kanivin.utils.pdf.pdf_footer_html"

# permissions

permission_query_conditions = {
	"Event": "kanivin.desk.doctype.event.event.get_permission_query_conditions",
	"ToDo": "kanivin.desk.doctype.todo.todo.get_permission_query_conditions",
	"User": "kanivin.core.doctype.user.user.get_permission_query_conditions",
	"Dashboard Settings": "kanivin.desk.doctype.dashboard_settings.dashboard_settings.get_permission_query_conditions",
	"Notification Log": "kanivin.desk.doctype.notification_log.notification_log.get_permission_query_conditions",
	"Dashboard": "kanivin.desk.doctype.dashboard.dashboard.get_permission_query_conditions",
	"Dashboard Chart": "kanivin.desk.doctype.dashboard_chart.dashboard_chart.get_permission_query_conditions",
	"Number Card": "kanivin.desk.doctype.number_card.number_card.get_permission_query_conditions",
	"Notification Settings": "kanivin.desk.doctype.notification_settings.notification_settings.get_permission_query_conditions",
	"Note": "kanivin.desk.doctype.note.note.get_permission_query_conditions",
	"Kanban Board": "kanivin.desk.doctype.kanban_board.kanban_board.get_permission_query_conditions",
	"Contact": "kanivin.contacts.address_and_contact.get_permission_query_conditions_for_contact",
	"Address": "kanivin.contacts.address_and_contact.get_permission_query_conditions_for_address",
	"Communication": "kanivin.core.doctype.communication.communication.get_permission_query_conditions_for_communication",
	"Workflow Action": "kanivin.workflow.doctype.workflow_action.workflow_action.get_permission_query_conditions",
	"Prepared Report": "kanivin.core.doctype.prepared_report.prepared_report.get_permission_query_condition",
	"File": "kanivin.core.doctype.file.file.get_permission_query_conditions",
}

has_permission = {
	"Event": "kanivin.desk.doctype.event.event.has_permission",
	"ToDo": "kanivin.desk.doctype.todo.todo.has_permission",
	"Note": "kanivin.desk.doctype.note.note.has_permission",
	"User": "kanivin.core.doctype.user.user.has_permission",
	"Dashboard Chart": "kanivin.desk.doctype.dashboard_chart.dashboard_chart.has_permission",
	"Number Card": "kanivin.desk.doctype.number_card.number_card.has_permission",
	"Kanban Board": "kanivin.desk.doctype.kanban_board.kanban_board.has_permission",
	"Contact": "kanivin.contacts.address_and_contact.has_permission",
	"Address": "kanivin.contacts.address_and_contact.has_permission",
	"Communication": "kanivin.core.doctype.communication.communication.has_permission",
	"Workflow Action": "kanivin.workflow.doctype.workflow_action.workflow_action.has_permission",
	"File": "kanivin.core.doctype.file.file.has_permission",
	"Prepared Report": "kanivin.core.doctype.prepared_report.prepared_report.has_permission",
	"Notification Settings": "kanivin.desk.doctype.notification_settings.notification_settings.has_permission",
}

has_website_permission = {"Address": "kanivin.contacts.doctype.address.address.has_website_permission"}

jinja = {
	"methods": "kanivin.utils.jinja_globals",
	"filters": [
		"kanivin.utils.data.global_date_format",
		"kanivin.utils.markdown",
		"kanivin.website.utils.abs_url",
	],
}

standard_queries = {"User": "kanivin.core.doctype.user.user.user_query"}

doc_events = {
	"*": {
		"on_update": [
			"kanivin.desk.notifications.clear_doctype_notifications",
			"kanivin.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"kanivin.core.doctype.file.utils.attach_files_to_document",
			"kanivin.automation.doctype.assignment_rule.assignment_rule.apply",
			"kanivin.automation.doctype.assignment_rule.assignment_rule.update_due_date",
			"kanivin.core.doctype.user_type.user_type.apply_permissions_for_non_standard_user_type",
		],
		"after_rename": "kanivin.desk.notifications.clear_doctype_notifications",
		"on_cancel": [
			"kanivin.desk.notifications.clear_doctype_notifications",
			"kanivin.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"kanivin.automation.doctype.assignment_rule.assignment_rule.apply",
		],
		"on_trash": [
			"kanivin.desk.notifications.clear_doctype_notifications",
			"kanivin.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
		],
		"on_update_after_submit": [
			"kanivin.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"kanivin.automation.doctype.assignment_rule.assignment_rule.apply",
			"kanivin.automation.doctype.assignment_rule.assignment_rule.update_due_date",
			"kanivin.core.doctype.file.utils.attach_files_to_document",
		],
		"on_change": [
			"kanivin.social.doctype.energy_point_rule.energy_point_rule.process_energy_points",
			"kanivin.automation.doctype.milestone_tracker.milestone_tracker.evaluate_milestone",
		],
	},
	"Event": {
		"after_insert": "kanivin.integrations.doctype.google_calendar.google_calendar.insert_event_in_google_calendar",
		"on_update": "kanivin.integrations.doctype.google_calendar.google_calendar.update_event_in_google_calendar",
		"on_trash": "kanivin.integrations.doctype.google_calendar.google_calendar.delete_event_from_google_calendar",
	},
	"Contact": {
		"after_insert": "kanivin.integrations.doctype.google_contacts.google_contacts.insert_contacts_to_google_contacts",
		"on_update": "kanivin.integrations.doctype.google_contacts.google_contacts.update_contacts_to_google_contacts",
	},
	"DocType": {
		"on_update": "kanivin.cache_manager.build_domain_restriced_doctype_cache",
	},
	"Page": {
		"on_update": "kanivin.cache_manager.build_domain_restriced_page_cache",
	},
}

scheduler_events = {
	"cron": {
		# 15 minutes
		"0/15 * * * *": [
			"kanivin.oauth.delete_oauth2_data",
			"kanivin.website.doctype.web_page.web_page.check_publish_status",
			"kanivin.twofactor.delete_all_barcodes_for_users",
			"kanivin.email.doctype.email_account.email_account.notify_unreplied",
			"kanivin.utils.global_search.sync_global_search",
			"kanivin.deferred_insert.save_to_db",
			"kanivin.automation.doctype.reminder.reminder.send_reminders",
		],
		# 10 minutes
		"0/10 * * * *": [
			"kanivin.email.doctype.email_account.email_account.pull",
		],
		# Hourly but offset by 30 minutes
		"30 * * * *": [
			"kanivin.core.doctype.prepared_report.prepared_report.expire_stalled_report",
		],
		# Daily but offset by 45 minutes
		"45 0 * * *": [
			"kanivin.core.doctype.log_settings.log_settings.run_log_clean_up",
		],
	},
	"all": [
		"kanivin.email.queue.flush",
		"kanivin.monitor.flush",
		"kanivin.integrations.doctype.google_calendar.google_calendar.sync",
	],
	"hourly": [
		"kanivin.model.utils.link_count.update_link_count",
		"kanivin.model.utils.user_settings.sync_user_settings",
		"kanivin.desk.page.backups.backups.delete_downloadable_backups",
		"kanivin.desk.form.document_follow.send_hourly_updates",
		"kanivin.email.doctype.newsletter.newsletter.send_scheduled_email",
		"kanivin.website.doctype.personal_data_deletion_request.personal_data_deletion_request.process_data_deletion_request",
	],
	"daily": [
		"kanivin.desk.notifications.clear_notifications",
		"kanivin.desk.doctype.event.event.send_event_digest",
		"kanivin.sessions.clear_expired_sessions",
		"kanivin.email.doctype.notification.notification.trigger_daily_alerts",
		"kanivin.website.doctype.personal_data_deletion_request.personal_data_deletion_request.remove_unverified_record",
		"kanivin.desk.form.document_follow.send_daily_updates",
		"kanivin.social.doctype.energy_point_settings.energy_point_settings.allocate_review_points",
		"kanivin.integrations.doctype.google_contacts.google_contacts.sync",
		"kanivin.automation.doctype.auto_repeat.auto_repeat.make_auto_repeat_entry",
	],
	"daily_long": [
		"kanivin.integrations.doctype.dropbox_settings.dropbox_settings.take_backups_daily",
		"kanivin.integrations.doctype.s3_backup_settings.s3_backup_settings.take_backups_daily",
		"kanivin.email.doctype.auto_email_report.auto_email_report.send_daily",
		"kanivin.integrations.doctype.google_drive.google_drive.daily_backup",
	],
	"weekly_long": [
		"kanivin.integrations.doctype.dropbox_settings.dropbox_settings.take_backups_weekly",
		"kanivin.integrations.doctype.s3_backup_settings.s3_backup_settings.take_backups_weekly",
		"kanivin.desk.form.document_follow.send_weekly_updates",
		"kanivin.utils.change_log.check_for_update",
		"kanivin.social.doctype.energy_point_log.energy_point_log.send_weekly_summary",
		"kanivin.integrations.doctype.google_drive.google_drive.weekly_backup",
		"kanivin.desk.doctype.changelog_feed.changelog_feed.fetch_changelog_feed",
	],
	"monthly": [
		"kanivin.email.doctype.auto_email_report.auto_email_report.send_monthly",
		"kanivin.social.doctype.energy_point_log.energy_point_log.send_monthly_summary",
	],
	"monthly_long": [
		"kanivin.integrations.doctype.s3_backup_settings.s3_backup_settings.take_backups_monthly"
	],
}

sounds = [
	{"name": "email", "src": "/assets/kanivin/sounds/email.mp3", "volume": 0.1},
	{"name": "submit", "src": "/assets/kanivin/sounds/submit.mp3", "volume": 0.1},
	{"name": "cancel", "src": "/assets/kanivin/sounds/cancel.mp3", "volume": 0.1},
	{"name": "delete", "src": "/assets/kanivin/sounds/delete.mp3", "volume": 0.05},
	{"name": "click", "src": "/assets/kanivin/sounds/click.mp3", "volume": 0.05},
	{"name": "error", "src": "/assets/kanivin/sounds/error.mp3", "volume": 0.1},
	{"name": "alert", "src": "/assets/kanivin/sounds/alert.mp3", "volume": 0.2},
	# {"name": "chime", "src": "/assets/kanivin/sounds/chime.mp3"},
]

setup_wizard_exception = [
	"kanivin.desk.page.setup_wizard.setup_wizard.email_setup_wizard_exception",
	"kanivin.desk.page.setup_wizard.setup_wizard.log_setup_wizard_exception",
]

before_migrate = ["kanivin.core.doctype.patch_log.patch_log.before_migrate"]
after_migrate = ["kanivin.website.doctype.website_theme.website_theme.after_migrate"]

otp_methods = ["OTP App", "Email", "SMS"]

user_data_fields = [
	{"doctype": "Access Log", "strict": True},
	{"doctype": "Activity Log", "strict": True},
	{"doctype": "Comment", "strict": True},
	{
		"doctype": "Contact",
		"filter_by": "email_id",
		"redact_fields": ["first_name", "last_name", "phone", "mobile_no"],
		"rename": True,
	},
	{"doctype": "Contact Email", "filter_by": "email_id"},
	{
		"doctype": "Address",
		"filter_by": "email_id",
		"redact_fields": [
			"address_title",
			"address_line1",
			"address_line2",
			"city",
			"county",
			"state",
			"pincode",
			"phone",
			"fax",
		],
	},
	{
		"doctype": "Communication",
		"filter_by": "sender",
		"redact_fields": ["sender_full_name", "phone_no", "content"],
	},
	{"doctype": "Communication", "filter_by": "recipients"},
	{"doctype": "Email Group Member", "filter_by": "email"},
	{"doctype": "Email Unsubscribe", "filter_by": "email", "partial": True},
	{"doctype": "Email Queue", "filter_by": "sender"},
	{"doctype": "Email Queue Recipient", "filter_by": "recipient"},
	{
		"doctype": "File",
		"filter_by": "attached_to_name",
		"redact_fields": ["file_name", "file_url"],
	},
	{
		"doctype": "User",
		"filter_by": "name",
		"redact_fields": [
			"email",
			"username",
			"first_name",
			"middle_name",
			"last_name",
			"full_name",
			"birth_date",
			"user_image",
			"phone",
			"mobile_no",
			"location",
			"banner_image",
			"interest",
			"bio",
			"email_signature",
		],
	},
	{"doctype": "Version", "strict": True},
]

global_search_doctypes = {
	"Default": [
		{"doctype": "Contact"},
		{"doctype": "Address"},
		{"doctype": "ToDo"},
		{"doctype": "Note"},
		{"doctype": "Event"},
		{"doctype": "Blog Post"},
		{"doctype": "Dashboard"},
		{"doctype": "Country"},
		{"doctype": "Currency"},
		{"doctype": "Newsletter"},
		{"doctype": "Letter Head"},
		{"doctype": "Workflow"},
		{"doctype": "Web Page"},
		{"doctype": "Web Form"},
	]
}

override_whitelisted_methods = {
	# Legacy File APIs
	"kanivin.utils.file_manager.download_file": "download_file",
	"kanivin.core.doctype.file.file.download_file": "download_file",
	"kanivin.core.doctype.file.file.unzip_file": "kanivin.core.api.file.unzip_file",
	"kanivin.core.doctype.file.file.get_attached_images": "kanivin.core.api.file.get_attached_images",
	"kanivin.core.doctype.file.file.get_files_in_folder": "kanivin.core.api.file.get_files_in_folder",
	"kanivin.core.doctype.file.file.get_files_by_search_text": "kanivin.core.api.file.get_files_by_search_text",
	"kanivin.core.doctype.file.file.get_max_file_size": "kanivin.core.api.file.get_max_file_size",
	"kanivin.core.doctype.file.file.create_new_folder": "kanivin.core.api.file.create_new_folder",
	"kanivin.core.doctype.file.file.move_file": "kanivin.core.api.file.move_file",
	"kanivin.core.doctype.file.file.zip_files": "kanivin.core.api.file.zip_files",
	# Legacy (& Consistency) OAuth2 APIs
	"kanivin.www.login.login_via_google": "kanivin.integrations.oauth2_logins.login_via_google",
	"kanivin.www.login.login_via_github": "kanivin.integrations.oauth2_logins.login_via_github",
	"kanivin.www.login.login_via_facebook": "kanivin.integrations.oauth2_logins.login_via_facebook",
	"kanivin.www.login.login_via_kanivin": "kanivin.integrations.oauth2_logins.login_via_kanivin",
	"kanivin.www.login.login_via_office365": "kanivin.integrations.oauth2_logins.login_via_office365",
	"kanivin.www.login.login_via_salesforce": "kanivin.integrations.oauth2_logins.login_via_salesforce",
	"kanivin.www.login.login_via_fairlogin": "kanivin.integrations.oauth2_logins.login_via_fairlogin",
}

ignore_links_on_delete = [
	"Communication",
	"ToDo",
	"DocShare",
	"Email Unsubscribe",
	"Activity Log",
	"File",
	"Version",
	"Document Follow",
	"Comment",
	"View Log",
	"Tag Link",
	"Notification Log",
	"Email Queue",
	"Document Share Key",
	"Integration Request",
	"Unhandled Email",
	"Webhook Request Log",
	"Workspace",
	"Route History",
	"Access Log",
]

# Request Hooks
before_request = [
	"kanivin.recorder.record",
	"kanivin.monitor.start",
	"kanivin.rate_limiter.apply",
]

after_request = [
	"kanivin.monitor.stop",
]

# Background Job Hooks
before_job = [
	"kanivin.recorder.record",
	"kanivin.monitor.start",
]

if os.getenv("FRAPPE_SENTRY_DSN") and (
	os.getenv("ENABLE_SENTRY_DB_MONITORING")
	or os.getenv("SENTRY_TRACING_SAMPLE_RATE")
	or os.getenv("SENTRY_PROFILING_SAMPLE_RATE")
):
	before_request.append("kanivin.utils.sentry.set_sentry_context")
	before_job.append("kanivin.utils.sentry.set_sentry_context")

after_job = [
	"kanivin.recorder.dump",
	"kanivin.monitor.stop",
	"kanivin.utils.file_lock.release_document_locks",
]

extend_bootinfo = [
	"kanivin.utils.telemetry.add_bootinfo",
	"kanivin.core.doctype.user_permission.user_permission.send_user_permissions",
]

get_changelog_feed = "kanivin.desk.doctype.changelog_feed.changelog_feed.get_feed"

export_python_type_annotations = True

standard_navbar_items = [
	{
		"item_label": "My Profile",
		"item_type": "Route",
		"route": "/app/user-profile",
		"is_standard": 1,
	},
	{
		"item_label": "My Settings",
		"item_type": "Action",
		"action": "kanivin.ui.toolbar.route_to_user()",
		"is_standard": 1,
	},
	{
		"item_label": "Session Defaults",
		"item_type": "Action",
		"action": "kanivin.ui.toolbar.setup_session_defaults()",
		"is_standard": 1,
	},
	{
		"item_label": "Reload",
		"item_type": "Action",
		"action": "kanivin.ui.toolbar.clear_cache()",
		"is_standard": 1,
	},
	{
		"item_label": "View Website",
		"item_type": "Action",
		"action": "kanivin.ui.toolbar.view_website()",
		"is_standard": 1,
	},
	{
		"item_label": "Apps",
		"item_type": "Route",
		"route": "/apps",
		"is_standard": 1,
	},
	{
		"item_label": "Toggle Full Width",
		"item_type": "Action",
		"action": "kanivin.ui.toolbar.toggle_full_width()",
		"is_standard": 1,
	},
	{
		"item_label": "Toggle Theme",
		"item_type": "Action",
		"action": "new kanivin.ui.ThemeSwitcher().show()",
		"is_standard": 1,
	},
	{
		"item_type": "Separator",
		"is_standard": 1,
		"item_label": "",
	},
	{
		"item_label": "Log out",
		"item_type": "Action",
		"action": "kanivin.app.logout()",
		"is_standard": 1,
	},
]

standard_help_items = [
	{
		"item_label": "About",
		"item_type": "Action",
		"action": "kanivin.ui.toolbar.show_about()",
		"is_standard": 1,
	},
	{
		"item_label": "Keyboard Shortcuts",
		"item_type": "Action",
		"action": "kanivin.ui.toolbar.show_shortcuts(event)",
		"is_standard": 1,
	},
	{
		"item_label": "Kanivin Support",
		"item_type": "Route",
		"route": "https://kanivin.io/support",
		"is_standard": 1,
	},
]

# log doctype cleanups to automatically add in log settings
default_log_clearing_doctypes = {
	"Error Log": 14,
	"Email Queue": 30,
	"Scheduled Job Log": 7,
	"Submission Queue": 7,
	"Prepared Report": 14,
	"Webhook Request Log": 30,
	"Unhandled Email": 30,
	"Reminder": 30,
	"Integration Request": 90,
	"Activity Log": 90,
	"Route History": 90,
}

# These keys will not be erased when doing kanivin.clear_cache()
persistent_cache_keys = [
	"changelog-*",  # version update notifications
	"insert_queue_for_*",  # Deferred Insert
	"recorder-*",  # Recorder
	"global_search_queue",
	"monitor-transactions",
	"rate-limit-counter-*",
	"rl:*",
]
