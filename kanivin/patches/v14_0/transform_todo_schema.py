import kanivin
from kanivin.query_builder.utils import DocType


def execute():
	# Email Template & Help Article have owner field that doesn't have any additional functionality
	# Only ToDo has to be updated.

	ToDo = DocType("ToDo")
	kanivin.reload_doctype("ToDo", force=True)

	kanivin.qb.update(ToDo).set(ToDo.allocated_to, ToDo.owner).run()
