# Copyright (c) 2019, Kanivin and Contributors
# License: MIT. See LICENSE
import kanivin
import kanivin.cache_manager
from kanivin.tests.utils import KanivinTestCase


class TestMilestoneTracker(KanivinTestCase):
	def test_milestone(self):
		kanivin.db.delete("Milestone Tracker")

		kanivin.cache.delete_key("milestone_tracker_map")

		milestone_tracker = kanivin.get_doc(
			dict(doctype="Milestone Tracker", document_type="ToDo", track_field="status")
		).insert()

		todo = kanivin.get_doc(dict(doctype="ToDo", description="test milestone", status="Open")).insert()

		milestones = kanivin.get_all(
			"Milestone",
			fields=["track_field", "value", "milestone_tracker"],
			filters=dict(reference_type=todo.doctype, reference_name=todo.name),
		)

		self.assertEqual(len(milestones), 1)
		self.assertEqual(milestones[0].track_field, "status")
		self.assertEqual(milestones[0].value, "Open")

		todo.status = "Closed"
		todo.save()

		milestones = kanivin.get_all(
			"Milestone",
			fields=["track_field", "value", "milestone_tracker"],
			filters=dict(reference_type=todo.doctype, reference_name=todo.name),
			order_by="modified desc",
		)

		self.assertEqual(len(milestones), 2)
		self.assertEqual(milestones[0].track_field, "status")
		self.assertEqual(milestones[0].value, "Closed")

		# cleanup
		kanivin.db.delete("Milestone")
		milestone_tracker.delete()
