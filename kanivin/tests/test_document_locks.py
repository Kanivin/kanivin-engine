# Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import kanivin
from kanivin.tests.utils import KanivinTestCase
from kanivin.utils.data import add_to_date, today


class TestDocumentLocks(KanivinTestCase):
	def test_locking(self):
		todo = kanivin.get_doc(dict(doctype="ToDo", description="test")).insert()
		todo_1 = kanivin.get_doc("ToDo", todo.name)

		todo.lock()
		self.assertRaises(kanivin.DocumentLockedError, todo_1.lock)
		todo.unlock()

		todo_1.lock()
		self.assertRaises(kanivin.DocumentLockedError, todo.lock)
		todo_1.unlock()

	def test_operations_on_locked_documents(self):
		todo = kanivin.get_doc(dict(doctype="ToDo", description="testing operations")).insert()
		todo.lock()

		with self.assertRaises(kanivin.DocumentLockedError):
			todo.description = "Random"
			todo.save()

		# Checking for persistant locks across all instances.
		doc = kanivin.get_doc("ToDo", todo.name)
		self.assertEqual(doc.is_locked, True)

		with self.assertRaises(kanivin.DocumentLockedError):
			doc.description = "Random"
			doc.save()

		doc.unlock()
		self.assertEqual(doc.is_locked, False)
		self.assertEqual(todo.is_locked, False)

	def test_locks_auto_expiry(self):
		todo = kanivin.get_doc(dict(doctype="ToDo", description=kanivin.generate_hash())).insert()
		todo.lock()

		self.assertRaises(kanivin.DocumentLockedError, todo.lock)

		with self.freeze_time(add_to_date(today(), days=3)):
			todo.lock()
