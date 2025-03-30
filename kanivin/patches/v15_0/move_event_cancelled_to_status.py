import kanivin


def execute():
	Event = kanivin.qb.DocType("Event")
	query = (
		kanivin.qb.update(Event)
		.set(Event.event_type, "Private")
		.set(Event.status, "Cancelled")
		.where(Event.event_type == "Cancelled")
	)
	query.run()
