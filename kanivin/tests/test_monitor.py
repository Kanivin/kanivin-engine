# Copyright (c) 2020, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import kanivin
import kanivin.monitor
from kanivin.monitor import MONITOR_REDIS_KEY, get_trace_id
from kanivin.tests.utils import KanivinTestCase
from kanivin.utils import set_request
from kanivin.utils.response import build_response


class TestMonitor(KanivinTestCase):
	def setUp(self):
		kanivin.conf.monitor = 1
		kanivin.cache.delete_value(MONITOR_REDIS_KEY)

	def tearDown(self):
		kanivin.conf.monitor = 0
		kanivin.cache.delete_value(MONITOR_REDIS_KEY)

	def test_enable_monitor(self):
		set_request(method="GET", path="/api/method/kanivin.ping")
		response = build_response("json")

		kanivin.monitor.start()
		kanivin.monitor.stop(response)

		logs = kanivin.cache.lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)

		log = kanivin.parse_json(logs[0].decode())
		self.assertTrue(log.duration)
		self.assertTrue(log.site)
		self.assertTrue(log.timestamp)
		self.assertTrue(log.uuid)
		self.assertTrue(log.request)
		self.assertEqual(log.transaction_type, "request")
		self.assertEqual(log.request["method"], "GET")

	def test_no_response(self):
		set_request(method="GET", path="/api/method/kanivin.ping")

		kanivin.monitor.start()
		kanivin.monitor.stop(response=None)

		logs = kanivin.cache.lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)

		log = kanivin.parse_json(logs[0].decode())
		self.assertEqual(log.request["status_code"], 500)
		self.assertEqual(log.transaction_type, "request")
		self.assertEqual(log.request["method"], "GET")

	def test_job(self):
		kanivin.utils.background_jobs.execute_job(
			kanivin.local.site, "kanivin.ping", None, None, {}, is_async=False
		)

		logs = kanivin.cache.lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)
		log = kanivin.parse_json(logs[0].decode())
		self.assertEqual(log.transaction_type, "job")
		self.assertTrue(log.job)
		self.assertEqual(log.job["method"], "kanivin.ping")
		self.assertEqual(log.job["scheduled"], False)
		self.assertEqual(log.job["wait"], 0)

	def test_flush(self):
		set_request(method="GET", path="/api/method/kanivin.ping")
		response = build_response("json")
		kanivin.monitor.start()
		kanivin.monitor.stop(response)

		open(kanivin.monitor.log_file(), "w").close()
		kanivin.monitor.flush()

		with open(kanivin.monitor.log_file()) as f:
			logs = f.readlines()

		self.assertEqual(len(logs), 1)
		log = kanivin.parse_json(logs[0])
		self.assertEqual(log.transaction_type, "request")

	def test_trace_ids(self):
		set_request(method="GET", path="/api/method/kanivin.ping")
		response = build_response("json")
		kanivin.monitor.start()
		kanivin.db.sql("select 1")
		self.assertIn(get_trace_id(), str(kanivin.db.last_query))
		kanivin.monitor.stop(response)
