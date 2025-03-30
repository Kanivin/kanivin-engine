# Copyright (c) 2017, Kanivin and contributors
# License: MIT. See LICENSE

from collections import defaultdict

import kanivin
from kanivin.model.document import Document


class RoleProfile(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from kanivin.core.doctype.has_role.has_role import HasRole
		from kanivin.types import DF

		role_profile: DF.Data
		roles: DF.Table[HasRole]

	# end: auto-generated types
	def autoname(self):
		"""set name as Role Profile name"""
		self.name = self.role_profile

	def on_update(self):
		self.clear_cache()
		self.queue_action(
			"update_all_users",
			now=kanivin.flags.in_test or kanivin.flags.in_install,
			enqueue_after_commit=True,
		)

	def update_all_users(self):
		"""Changes in role_profile reflected across all its user"""
		has_role = kanivin.qb.DocType("Has Role")
		user = kanivin.qb.DocType("User")

		all_current_roles = (
			kanivin.qb.from_(user)
			.join(has_role)
			.on(user.name == has_role.parent)
			.where(user.role_profile_name == self.name)
			.select(user.name, has_role.role)
		).run()

		user_roles = defaultdict(set)
		for user, role in all_current_roles:
			user_roles[user].add(role)

		role_profile_roles = {role.role for role in self.roles}
		for user, roles in user_roles.items():
			if roles != role_profile_roles:
				user = kanivin.get_doc("User", user)
				user.roles = []
				user.add_roles(*role_profile_roles)
