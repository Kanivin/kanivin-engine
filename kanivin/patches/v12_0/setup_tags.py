import kanivin


def execute():
	kanivin.delete_doc_if_exists("DocType", "Tag Category")
	kanivin.delete_doc_if_exists("DocType", "Tag Doc Category")

	kanivin.reload_doc("desk", "doctype", "tag")
	kanivin.reload_doc("desk", "doctype", "tag_link")

	tag_list = []
	tag_links = []
	time = kanivin.utils.get_datetime()

	for doctype in kanivin.get_list("DocType", filters={"istable": 0, "issingle": 0, "is_virtual": 0}):
		if not kanivin.db.count(doctype.name) or not kanivin.db.has_column(doctype.name, "_user_tags"):
			continue

		for _user_tags in kanivin.db.sql(
			f"select `name`, `_user_tags` from `tab{doctype.name}`", as_dict=True
		):
			if not _user_tags.get("_user_tags"):
				continue

			for tag in _user_tags.get("_user_tags").split(",") if _user_tags.get("_user_tags") else []:
				if not tag:
					continue

				tag_list.append((tag.strip(), time, time, "Administrator"))

				tag_link_name = kanivin.generate_hash(length=10)
				tag_links.append(
					(tag_link_name, doctype.name, _user_tags.name, tag.strip(), time, time, "Administrator")
				)

	kanivin.db.bulk_insert(
		"Tag",
		fields=["name", "creation", "modified", "modified_by"],
		values=set(tag_list),
		ignore_duplicates=True,
	)
	kanivin.db.bulk_insert(
		"Tag Link",
		fields=["name", "document_type", "document_name", "tag", "creation", "modified", "modified_by"],
		values=set(tag_links),
		ignore_duplicates=True,
	)
