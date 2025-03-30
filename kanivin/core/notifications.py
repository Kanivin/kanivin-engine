# Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import kanivin


def get_notification_config():
	return {
		"for_doctype": {
			"Error Log": {"seen": 0},
			"Communication": {"status": "Open", "communication_type": "Communication"},
			"ToDo": "kanivin.core.notifications.get_things_todo",
			"Event": "kanivin.core.notifications.get_todays_events",
			"Workflow Action": {"status": "Open"},
		},
	}


def get_things_todo(as_list=False):
	"""Returns a count of incomplete todos"""
	data = kanivin.get_list(
		"ToDo",
		fields=["name", "description"] if as_list else "count(*)",
		filters=[["ToDo", "status", "=", "Open"]],
		or_filters=[
			["ToDo", "allocated_to", "=", kanivin.session.user],
			["ToDo", "assigned_by", "=", kanivin.session.user],
		],
		as_list=True,
	)

	if as_list:
		return data
	return data[0][0]


def get_todays_events(as_list: bool = False):
	"""Returns a count of todays events in calendar"""
	from kanivin.desk.doctype.event.event import get_events
	from kanivin.utils import nowdate

	today = nowdate()
	events = get_events(today, today)
	return events if as_list else len(events)
