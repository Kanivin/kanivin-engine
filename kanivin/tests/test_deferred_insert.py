import kanivin
from kanivin.deferred_insert import deferred_insert, save_to_db
from kanivin.tests.utils import KanivinTestCase


class TestDeferredInsert(KanivinTestCase):
	def test_deferred_insert(self):
		route_history = {"route": kanivin.generate_hash(), "user": "Administrator"}
		deferred_insert("Route History", [route_history])

		save_to_db()
		self.assertTrue(kanivin.db.exists("Route History", route_history))

		route_history = {"route": kanivin.generate_hash(), "user": "Administrator"}
		deferred_insert("Route History", [route_history])
		kanivin.clear_cache()  # deferred_insert cache keys are supposed to be persistent
		save_to_db()
		self.assertTrue(kanivin.db.exists("Route History", route_history))
