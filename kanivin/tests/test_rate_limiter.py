# Copyright (c) 2020, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import time

from werkzeug.wrappers import Response

import kanivin
import kanivin.rate_limiter
from kanivin.rate_limiter import RateLimiter
from kanivin.tests.utils import KanivinTestCase
from kanivin.utils import cint


class TestRateLimiter(KanivinTestCase):
	def test_apply_with_limit(self):
		kanivin.conf.rate_limit = {"window": 86400, "limit": 1}
		kanivin.rate_limiter.apply()

		self.assertTrue(hasattr(kanivin.local, "rate_limiter"))
		self.assertIsInstance(kanivin.local.rate_limiter, RateLimiter)

		kanivin.cache.delete(kanivin.local.rate_limiter.key)
		delattr(kanivin.local, "rate_limiter")

	def test_apply_without_limit(self):
		kanivin.conf.rate_limit = None
		kanivin.rate_limiter.apply()

		self.assertFalse(hasattr(kanivin.local, "rate_limiter"))

	def test_respond_over_limit(self):
		limiter = RateLimiter(1, 86400)
		time.sleep(1)
		limiter.update()

		kanivin.conf.rate_limit = {"window": 86400, "limit": 1}
		self.assertRaises(kanivin.TooManyRequestsError, kanivin.rate_limiter.apply)
		kanivin.rate_limiter.update()

		response = kanivin.rate_limiter.respond()

		self.assertIsInstance(response, Response)
		self.assertEqual(response.status_code, 429)

		headers = kanivin.local.rate_limiter.headers()
		self.assertIn("Retry-After", headers)
		self.assertIn("X-RateLimit-Reset", headers)
		self.assertIn("X-RateLimit-Limit", headers)
		self.assertIn("X-RateLimit-Remaining", headers)
		self.assertTrue(int(headers["X-RateLimit-Reset"]) <= 86400)
		self.assertEqual(int(headers["X-RateLimit-Limit"]), 1000000)
		self.assertEqual(int(headers["X-RateLimit-Remaining"]), 0)

		kanivin.cache.delete(limiter.key)
		kanivin.cache.delete(kanivin.local.rate_limiter.key)
		delattr(kanivin.local, "rate_limiter")

	def test_respond_under_limit(self):
		kanivin.conf.rate_limit = {"window": 86400, "limit": 0.01}
		kanivin.rate_limiter.apply()
		kanivin.rate_limiter.update()
		response = kanivin.rate_limiter.respond()
		self.assertEqual(response, None)

		kanivin.cache.delete(kanivin.local.rate_limiter.key)
		delattr(kanivin.local, "rate_limiter")

	def test_headers_under_limit(self):
		kanivin.conf.rate_limit = {"window": 86400, "limit": 1}
		kanivin.rate_limiter.apply()
		kanivin.rate_limiter.update()
		headers = kanivin.local.rate_limiter.headers()
		self.assertNotIn("Retry-After", headers)
		self.assertIn("X-RateLimit-Reset", headers)
		self.assertTrue(int(headers["X-RateLimit-Reset"] < 86400))
		self.assertEqual(int(headers["X-RateLimit-Limit"]), 1000000)
		self.assertEqual(int(headers["X-RateLimit-Remaining"]), 1000000)

		kanivin.cache.delete(kanivin.local.rate_limiter.key)
		delattr(kanivin.local, "rate_limiter")

	def test_reject_over_limit(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		limiter = RateLimiter(0.01, 86400)
		self.assertRaises(kanivin.TooManyRequestsError, limiter.apply)

		kanivin.cache.delete(limiter.key)

	def test_do_not_reject_under_limit(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		limiter = RateLimiter(0.02, 86400)
		self.assertEqual(limiter.apply(), None)

		kanivin.cache.delete(limiter.key)

	def test_update_method(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		self.assertEqual(limiter.duration, cint(kanivin.cache.get(limiter.key)))

		kanivin.cache.delete(limiter.key)

	def test_window_expires(self):
		limiter = RateLimiter(1000, 1)
		self.assertTrue(kanivin.cache.exists(limiter.key, shared=True))
		limiter.update()
		self.assertTrue(kanivin.cache.exists(limiter.key, shared=True))
		time.sleep(1.1)
		self.assertFalse(kanivin.cache.exists(limiter.key, shared=True))
		kanivin.cache.delete(limiter.key)
