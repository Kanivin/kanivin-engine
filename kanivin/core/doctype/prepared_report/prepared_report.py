# Copyright (c) 2018, Kanivin and contributors
# License: MIT. See LICENSE
import gzip
import json
import resource
from contextlib import suppress
from typing import Any

from rq import get_current_job

import kanivin
from kanivin.database.utils import dangerously_reconnect_on_connection_abort
from kanivin.desk.form.load import get_attachments
from kanivin.desk.query_report import generate_report_result
from kanivin.model.document import Document
from kanivin.monitor import add_data_to_monitor
from kanivin.utils import add_to_date, now
from kanivin.utils.background_jobs import enqueue

# If prepared report runs for longer than this time it's automatically considered as failed
FAILURE_THRESHOLD = 60 * 60
REPORT_TIMEOUT = 25 * 60


class PreparedReport(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from kanivin.types import DF

		error_message: DF.Text | None
		filters: DF.SmallText | None
		job_id: DF.Data | None
		peak_memory_usage: DF.Int
		queued_at: DF.Datetime | None
		queued_by: DF.Data | None
		report_end_time: DF.Datetime | None
		report_name: DF.Data
		status: DF.Literal["Error", "Queued", "Completed", "Started"]

	# end: auto-generated types
	@property
	def queued_by(self):
		return self.owner

	@property
	def queued_at(self):
		return self.creation

	@staticmethod
	def clear_old_logs(days=30):
		prepared_reports_to_delete = kanivin.get_all(
			"Prepared Report",
			filters={"modified": ["<", kanivin.utils.add_days(kanivin.utils.now(), -days)]},
		)

		for batch in kanivin.utils.create_batch(prepared_reports_to_delete, 100):
			enqueue(method=delete_prepared_reports, reports=batch)

	def before_insert(self):
		self.status = "Queued"

	def on_trash(self):
		"""Remove pending job from queue, if already running then kill the job."""
		if self.status not in ("Started", "Queued"):
			return

		with suppress(Exception):
			job = kanivin.get_doc("RQ Job", self.job_id)
			job.stop_job() if self.status == "Started" else job.delete()

	def after_insert(self):
		timeout = kanivin.get_value("Report", self.report_name, "timeout")
		enqueue(
			generate_report,
			queue="long",
			prepared_report=self.name,
			timeout=timeout or REPORT_TIMEOUT,
			enqueue_after_commit=True,
		)

	def get_prepared_data(self, with_file_name=False):
		if attachments := get_attachments(self.doctype, self.name):
			attachment = attachments[0]
			attached_file = kanivin.get_doc("File", attachment.name)

			if with_file_name:
				return (gzip.decompress(attached_file.get_content()), attachment.file_name)
			return gzip.decompress(attached_file.get_content())


def generate_report(prepared_report):
	update_job_id(prepared_report)

	instance: PreparedReport = kanivin.get_doc("Prepared Report", prepared_report)
	report = kanivin.get_doc("Report", instance.report_name)

	add_data_to_monitor(report=instance.report_name)

	try:
		report.custom_columns = []

		if report.report_type == "Custom Report":
			custom_report_doc = report
			reference_report = custom_report_doc.reference_report
			report = kanivin.get_doc("Report", reference_report)
			if custom_report_doc.json:
				data = json.loads(custom_report_doc.json)
				if data:
					report.custom_columns = data["columns"]

		result = generate_report_result(report=report, filters=instance.filters, user=instance.owner)
		create_json_gz_file(result, instance.doctype, instance.name, instance.report_name)

		instance.status = "Completed"
	except Exception:
		# we need to ensure that error gets stored
		_save_error(instance, error=kanivin.get_traceback(with_context=True))

	instance.report_end_time = kanivin.utils.now()
	instance.peak_memory_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
	add_data_to_monitor(peak_memory_usage=instance.peak_memory_usage)
	instance.save(ignore_permissions=True)

	kanivin.publish_realtime(
		"report_generated",
		{"report_name": instance.report_name, "name": instance.name},
		user=kanivin.session.user,
	)


@dangerously_reconnect_on_connection_abort
def _save_error(instance, error):
	instance.reload()
	instance.status = "Error"
	instance.error_message = error
	instance.save(ignore_permissions=True)


def update_job_id(prepared_report):
	job = get_current_job()

	kanivin.db.set_value(
		"Prepared Report",
		prepared_report,
		{
			"job_id": job and job.id,
			"status": "Started",
		},
	)

	kanivin.db.commit()


@kanivin.whitelist()
def make_prepared_report(report_name, filters=None):
	"""run reports in background"""
	prepared_report = kanivin.get_doc(
		{
			"doctype": "Prepared Report",
			"report_name": report_name,
			"filters": process_filters_for_prepared_report(filters),
		}
	).insert(ignore_permissions=True)

	return {"name": prepared_report.name}


def process_filters_for_prepared_report(filters: dict[str, Any] | str) -> str:
	if isinstance(filters, str):
		filters = json.loads(filters)

	# This looks like an insanity but, without this it'd be very hard to find Prepared Reports matching given condition
	# We're ensuring that spacing is consistent. e.g. JS seems to put no spaces after ":", Python on the other hand does.
	# We are also ensuring that order of keys is same so generated JSON string will be identical too.
	# PS: kanivin.as_json sorts keys
	return kanivin.as_json(filters, indent=None, separators=(",", ":"))


@kanivin.whitelist()
def get_reports_in_queued_state(report_name, filters):
	return kanivin.get_all(
		"Prepared Report",
		filters={
			"report_name": report_name,
			"filters": process_filters_for_prepared_report(filters),
			"status": ("in", ("Queued", "Started")),
			"owner": kanivin.session.user,
		},
	)


def get_completed_prepared_report(filters, user, report_name):
	return kanivin.db.get_value(
		"Prepared Report",
		filters={
			"status": "Completed",
			"filters": process_filters_for_prepared_report(filters),
			"owner": user,
			"report_name": report_name,
		},
	)


def expire_stalled_report():
	kanivin.db.set_value(
		"Prepared Report",
		{
			"status": "Started",
			"modified": ("<", add_to_date(now(), seconds=-FAILURE_THRESHOLD, as_datetime=True)),
		},
		{
			"status": "Failed",
			"error_message": kanivin._("Report timed out."),
		},
		update_modified=False,
	)


@kanivin.whitelist()
def delete_prepared_reports(reports):
	reports = kanivin.parse_json(reports)
	for report in reports:
		prepared_report = kanivin.get_doc("Prepared Report", report["name"])
		if prepared_report.has_permission():
			prepared_report.delete(ignore_permissions=True, delete_permanently=True)


def create_json_gz_file(data, dt, dn, report_name):
	# Storing data in CSV file causes information loss
	# Reports like P&L Statement were completely unsuable because of this
	json_filename = "{}_{}.json.gz".format(
		kanivin.scrub(report_name), kanivin.utils.data.format_datetime(kanivin.utils.now(), "Y-m-d-H-M")
	)
	encoded_content = kanivin.safe_encode(kanivin.as_json(data, indent=None, separators=(",", ":")))
	compressed_content = gzip.compress(encoded_content)

	# Call save() file function to upload and attach the file
	_file = kanivin.get_doc(
		{
			"doctype": "File",
			"file_name": json_filename,
			"attached_to_doctype": dt,
			"attached_to_name": dn,
			"content": compressed_content,
			"is_private": 1,
		}
	)
	_file.save(ignore_permissions=True)


@kanivin.whitelist()
def download_attachment(dn):
	pr = kanivin.get_doc("Prepared Report", dn)
	if not pr.has_permission("read"):
		kanivin.throw(kanivin._("Cannot Download Report due to insufficient permissions"))

	data, file_name = pr.get_prepared_data(with_file_name=True)
	kanivin.local.response.filename = file_name[:-3]
	kanivin.local.response.filecontent = data
	kanivin.local.response.type = "binary"


def get_permission_query_condition(user):
	if not user:
		user = kanivin.session.user
	if user == "Administrator":
		return None

	from kanivin.utils.user import UserPermissions

	user = UserPermissions(user)

	if "System Manager" in user.roles:
		return None

	reports = [kanivin.db.escape(report) for report in user.get_all_reports().keys()]

	return """`tabPrepared Report`.report_name in ({reports})""".format(reports=",".join(reports))


def has_permission(doc, user):
	if not user:
		user = kanivin.session.user
	if user == "Administrator":
		return True

	from kanivin.utils.user import UserPermissions

	user = UserPermissions(user)

	if "System Manager" in user.roles:
		return True

	return doc.report_name in user.get_all_reports().keys()
