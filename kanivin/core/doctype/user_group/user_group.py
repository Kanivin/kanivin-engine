# Copyright (c) 2021, Kanivin and contributors
# License: MIT. See LICENSE

import kanivin

# import kanivin
from kanivin.model.document import Document


class UserGroup(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from kanivin.core.doctype.user_group_member.user_group_member import UserGroupMember
		from kanivin.types import DF

		user_group_members: DF.TableMultiSelect[UserGroupMember]

	# end: auto-generated types
	def after_insert(self):
		kanivin.cache.delete_key("user_groups")

	def on_trash(self):
		kanivin.cache.delete_key("user_groups")
