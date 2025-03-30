# Copyright (c) 2025, Kanivin and Contributors
# See license.txt

import kanivin
from kanivin.core.doctype.rq_worker.rq_worker import RQWorker
from kanivin.tests.utils import KanivinTestCase


class TestRQWorker(KanivinTestCase):
	def test_get_worker_list(self):
		workers = RQWorker.get_list({})
		self.assertGreaterEqual(len(workers), 1)
		self.assertTrue(any("short" in w.queue_type for w in workers))

	def test_worker_serialization(self):
		workers = RQWorker.get_list({})
		kanivin.get_doc("RQ Worker", workers[0].name)
