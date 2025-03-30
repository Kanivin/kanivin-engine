# Copyright (c) 2025, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import kanivin
from kanivin.model import is_default_field
from kanivin.query_builder import Order
from kanivin.query_builder.functions import Count
from kanivin.query_builder.terms import SubQuery
from kanivin.query_builder.utils import DocType


@kanivin.whitelist()
def get_list_settings(doctype):
	try:
		return kanivin.get_cached_doc("List View Settings", doctype)
	except kanivin.DoesNotExistError:
		kanivin.clear_messages()


@kanivin.whitelist()
def set_list_settings(doctype, values):
	try:
		doc = kanivin.get_doc("List View Settings", doctype)
	except kanivin.DoesNotExistError:
		doc = kanivin.new_doc("List View Settings")
		doc.name = doctype
		kanivin.clear_messages()
	doc.update(kanivin.parse_json(values))
	doc.save()


@kanivin.whitelist()
def get_group_by_count(doctype: str, current_filters: str, field: str) -> list[dict]:
	current_filters = kanivin.parse_json(current_filters)

	if field == "assigned_to":
		ToDo = DocType("ToDo")
		User = DocType("User")
		count = Count("*").as_("count")
		filtered_records = kanivin.qb.get_query(
			doctype,
			filters=current_filters,
			fields=["name"],
			validate_filters=True,
		)

		return (
			kanivin.qb.from_(ToDo)
			.from_(User)
			.select(ToDo.allocated_to.as_("name"), count)
			.where(
				(ToDo.status != "Cancelled")
				& (ToDo.allocated_to == User.name)
				& (User.user_type == "System User")
				& (ToDo.reference_name.isin(SubQuery(filtered_records)))
			)
			.groupby(ToDo.allocated_to)
			.orderby(count, order=Order.desc)
			.limit(50)
			.run(as_dict=True)
		)

	if not kanivin.get_meta(doctype).has_field(field) and not is_default_field(field):
		raise ValueError("Field does not belong to doctype")

	data = kanivin.get_list(
		doctype,
		filters=current_filters,
		group_by=f"`tab{doctype}`.{field}",
		fields=["count(*) as count", f"`{field}` as name"],
		order_by="count desc",
	)

	if field == "owner":
		owner_idx = None

		for idx, item in enumerate(data):
			if item.name == kanivin.session.user:
				owner_idx = idx
				break

		if owner_idx:
			data = [data.pop(owner_idx)] + data[0:49]
		else:
			data = data[0:50]
	else:
		data = data[0:50]

	return data
