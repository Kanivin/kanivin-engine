import unittest
from collections.abc import Callable
from datetime import time

import kanivin
from kanivin.query_builder import Case
from kanivin.query_builder.builder import Function
from kanivin.query_builder.custom import ConstantColumn
from kanivin.query_builder.functions import (
	Cast_,
	Coalesce,
	CombineDatetime,
	Date,
	GroupConcat,
	Match,
	Round,
	Truncate,
	UnixTimestamp,
)
from kanivin.query_builder.utils import db_type_is
from kanivin.tests.utils import KanivinTestCase


def run_only_if(dbtype: db_type_is) -> Callable:
	return unittest.skipIf(db_type_is(kanivin.conf.db_type) != dbtype, f"Only runs for {dbtype.value}")


@run_only_if(db_type_is.MARIADB)
class TestCustomFunctionsMariaDB(KanivinTestCase):
	def test_concat(self):
		self.assertEqual("GROUP_CONCAT('Notes')", GroupConcat("Notes").get_sql())

	def test_match(self):
		query = Match("Notes")
		with self.assertRaises(Exception):
			query.get_sql()
		query = query.Against("text")
		self.assertEqual(" MATCH('Notes') AGAINST ('+text*' IN BOOLEAN MODE)", query.get_sql())

	def test_constant_column(self):
		query = kanivin.qb.from_("DocType").select("name", ConstantColumn("John").as_("User"))
		self.assertEqual(query.get_sql(), "SELECT `name`,'John' `User` FROM `tabDocType`")

	def test_timestamp(self):
		note = kanivin.qb.DocType("Note")
		self.assertEqual(
			"TIMESTAMP(posting_date,posting_time)",
			CombineDatetime(note.posting_date, note.posting_time).get_sql(),
		)
		self.assertEqual(
			"TIMESTAMP('2021-01-01','00:00:21')", CombineDatetime("2021-01-01", "00:00:21").get_sql()
		)

		todo = kanivin.qb.DocType("ToDo")
		select_query = (
			kanivin.qb.from_(note)
			.join(todo)
			.on(todo.refernce_name == note.name)
			.select(CombineDatetime(note.posting_date, note.posting_time))
		)
		self.assertIn(
			"select timestamp(`tabnote`.`posting_date`,`tabnote`.`posting_time`)", str(select_query).lower()
		)

		select_query = select_query.orderby(CombineDatetime(note.posting_date, note.posting_time))
		self.assertIn(
			"order by timestamp(`tabnote`.`posting_date`,`tabnote`.`posting_time`)",
			str(select_query).lower(),
		)

		select_query = select_query.where(
			CombineDatetime(note.posting_date, note.posting_time) >= CombineDatetime("2021-01-01", "00:00:01")
		)
		self.assertIn(
			"timestamp(`tabnote`.`posting_date`,`tabnote`.`posting_time`)>=timestamp('2021-01-01','00:00:01')",
			str(select_query).lower(),
		)

		select_query = select_query.select(
			CombineDatetime(note.posting_date, note.posting_time, alias="timestamp")
		)
		self.assertIn(
			"timestamp(`tabnote`.`posting_date`,`tabnote`.`posting_time`) `timestamp`",
			str(select_query).lower(),
		)

	def test_unix_ts_mariadb(self):
		# Simple Query
		note = kanivin.qb.DocType("Note")
		self.assertEqual(
			"unix_timestamp(posting_date)",
			UnixTimestamp(note.posting_date).get_sql(),
		)

		# Complex multi table query
		todo = kanivin.qb.DocType("ToDo")
		select_query = (
			kanivin.qb.from_(note)
			.join(todo)
			.on(todo.refernce_name == note.name)
			.select(UnixTimestamp(note.posting_date))
		)
		self.assertIn("select unix_timestamp(`tabnote`.`posting_date`)", str(select_query).lower())

		# Order by
		select_query = select_query.orderby(UnixTimestamp(note.posting_date))
		self.assertIn(
			"order by unix_timestamp(`tabnote`.`posting_date`)",
			str(select_query).lower(),
		)

		# Function comparison
		select_query = select_query.where(UnixTimestamp(note.posting_date) >= UnixTimestamp("2021-01-01"))
		self.assertIn(
			"unix_timestamp(`tabnote`.`posting_date`)>=unix_timestamp('2021-01-01')",
			str(select_query).lower(),
		)

		# aliasing
		select_query = select_query.select(UnixTimestamp(note.posting_date, alias="unix_ts"))
		self.assertIn(
			"unix_timestamp(`tabnote`.`posting_date`) `unix_ts`",
			str(select_query).lower(),
		)

	def test_time(self):
		note = kanivin.qb.DocType("Note")
		self.assertEqual(
			"TIMESTAMP('2021-01-01','00:00:21')", CombineDatetime("2021-01-01", time(0, 0, 21)).get_sql()
		)

		select_query = kanivin.qb.from_(note).select(CombineDatetime(note.posting_date, note.posting_time))
		self.assertIn("select timestamp(`posting_date`,`posting_time`)", str(select_query).lower())

		select_query = select_query.where(
			CombineDatetime(note.posting_date, note.posting_time)
			>= CombineDatetime("2021-01-01", time(0, 0, 1))
		)
		self.assertIn(
			"timestamp(`posting_date`,`posting_time`)>=timestamp('2021-01-01','00:00:01')",
			str(select_query).lower(),
		)

	def test_cast(self):
		note = kanivin.qb.DocType("Note")
		self.assertEqual("CONCAT(name,'')", Cast_(note.name, "varchar").get_sql())
		self.assertEqual("CAST(name AS INTEGER)", Cast_(note.name, "integer").get_sql())
		self.assertEqual(
			kanivin.qb.from_("red").from_(note).select("other", Cast_(note.name, "varchar")).get_sql(),
			"SELECT `tabred`.`other`,CONCAT(`tabNote`.`name`,'') FROM `tabred`,`tabNote`",
		)

	def test_round(self):
		note = kanivin.qb.DocType("Note")

		query = kanivin.qb.from_(note).select(Round(note.price))
		self.assertEqual("select round(`price`,0) from `tabnote`", str(query).lower())

		query = kanivin.qb.from_(note).select(Round(note.price, 3))
		self.assertEqual("select round(`price`,3) from `tabnote`", str(query).lower())

	def test_truncate(self):
		note = kanivin.qb.DocType("Note")
		query = kanivin.qb.from_(note).select(Truncate(note.price, 3))
		self.assertEqual("select truncate(`price`,3) from `tabnote`", str(query).lower())


@run_only_if(db_type_is.POSTGRES)
class TestCustomFunctionsPostgres(KanivinTestCase):
	def test_concat(self):
		self.assertEqual("STRING_AGG('Notes',',')", GroupConcat("Notes").get_sql())

	def test_match(self):
		query = Match("Notes")
		self.assertEqual("TO_TSVECTOR('Notes')", query.get_sql())
		query = Match("Notes").Against("text")
		self.assertEqual("TO_TSVECTOR('Notes') @@ PLAINTO_TSQUERY('text')", query.get_sql())

	def test_constant_column(self):
		query = kanivin.qb.from_("DocType").select("name", ConstantColumn("John").as_("User"))
		self.assertEqual(query.get_sql(), 'SELECT "name",\'John\' "User" FROM "tabDocType"')

	def test_timestamp(self):
		note = kanivin.qb.DocType("Note")
		self.assertEqual(
			"posting_date+posting_time", CombineDatetime(note.posting_date, note.posting_time).get_sql()
		)
		self.assertEqual(
			"CAST('2021-01-01' AS DATE)+CAST('00:00:21' AS TIME)",
			CombineDatetime("2021-01-01", "00:00:21").get_sql(),
		)

		todo = kanivin.qb.DocType("ToDo")
		select_query = (
			kanivin.qb.from_(note)
			.join(todo)
			.on(todo.refernce_name == note.name)
			.select(CombineDatetime(note.posting_date, note.posting_time))
		)
		self.assertIn('select "tabnote"."posting_date"+"tabnote"."posting_time"', str(select_query).lower())

		select_query = select_query.orderby(CombineDatetime(note.posting_date, note.posting_time))
		self.assertIn('order by "tabnote"."posting_date"+"tabnote"."posting_time"', str(select_query).lower())

		select_query = select_query.where(
			CombineDatetime(note.posting_date, note.posting_time) >= CombineDatetime("2021-01-01", "00:00:01")
		)
		self.assertIn(
			"""where "tabnote"."posting_date"+"tabnote"."posting_time">=cast('2021-01-01' as date)+cast('00:00:01' as time)""",
			str(select_query).lower(),
		)

		select_query = select_query.select(
			CombineDatetime(note.posting_date, note.posting_time, alias="timestamp")
		)
		self.assertIn(
			'"tabnote"."posting_date"+"tabnote"."posting_time" "timestamp"', str(select_query).lower()
		)

	def test_unix_ts_postgres(self):
		# Simple Query
		note = kanivin.qb.DocType("Note")
		self.assertEqual(
			"extract(epoch from posting_date)",
			UnixTimestamp(note.posting_date).get_sql().lower(),
		)

		# Complex multi table query
		todo = kanivin.qb.DocType("ToDo")
		select_query = (
			kanivin.qb.from_(note)
			.join(todo)
			.on(todo.refernce_name == note.name)
			.select(UnixTimestamp(note.posting_date))
		)
		self.assertIn('extract(epoch from "tabnote"."posting_date")', str(select_query).lower())

		# Order by
		select_query = select_query.orderby(UnixTimestamp(note.posting_date))
		self.assertIn(
			'order by extract(epoch from "tabnote"."posting_date")',
			str(select_query).lower(),
		)

		# Function comparison
		select_query = select_query.where(
			UnixTimestamp(note.posting_date) >= UnixTimestamp(Date("2021-01-01"))
		)
		self.assertIn(
			'extract(epoch from "tabnote"."posting_date")>=extract(epoch from date(\'2021-01-01\'))',
			str(select_query).lower(),
		)

		# aliasing
		select_query = select_query.select(UnixTimestamp(note.posting_date, alias="unix_ts"))
		self.assertIn(
			'extract(epoch from "tabnote"."posting_date") "unix_ts"',
			str(select_query).lower(),
		)

	def test_time(self):
		note = kanivin.qb.DocType("Note")

		self.assertEqual(
			"CAST('2021-01-01' AS DATE)+CAST('00:00:21' AS TIME)",
			CombineDatetime("2021-01-01", time(0, 0, 21)).get_sql(),
		)

		select_query = kanivin.qb.from_(note).select(CombineDatetime(note.posting_date, note.posting_time))
		self.assertIn('select "posting_date"+"posting_time"', str(select_query).lower())

		select_query = select_query.where(
			CombineDatetime(note.posting_date, note.posting_time)
			>= CombineDatetime("2021-01-01", time(0, 0, 1))
		)
		self.assertIn(
			"""where "posting_date"+"posting_time">=cast('2021-01-01' as date)+cast('00:00:01' as time)""",
			str(select_query).lower(),
		)

	def test_cast(self):
		note = kanivin.qb.DocType("Note")
		self.assertEqual("CAST(name AS VARCHAR)", Cast_(note.name, "varchar").get_sql())
		self.assertEqual("CAST(name AS INTEGER)", Cast_(note.name, "integer").get_sql())
		self.assertEqual(
			kanivin.qb.from_("red").from_(note).select("other", Cast_(note.name, "varchar")).get_sql(),
			'SELECT "tabred"."other",CAST("tabNote"."name" AS VARCHAR) FROM "tabred","tabNote"',
		)

	def test_round(self):
		note = kanivin.qb.DocType("Note")

		query = kanivin.qb.from_(note).select(Round(note.price))
		self.assertEqual('select round("price",0) from "tabnote"', str(query).lower())

		query = kanivin.qb.from_(note).select(Round(note.price, 3))
		self.assertEqual('select round("price",3) from "tabnote"', str(query).lower())

	def test_truncate(self):
		note = kanivin.qb.DocType("Note")
		query = kanivin.qb.from_(note).select(Truncate(note.price, 3))
		self.assertEqual('select truncate("price",3) from "tabnote"', str(query).lower())


class TestBuilderBase:
	def test_adding_tabs(self):
		self.assertEqual("tabNotes", kanivin.qb.DocType("Notes").get_sql())
		self.assertEqual("__Auth", kanivin.qb.DocType("__Auth").get_sql())
		self.assertEqual("Notes", kanivin.qb.Table("Notes").get_sql())

	def test_run_patcher(self):
		query = kanivin.qb.from_("ToDo").select("*").limit(1)
		data = query.run(as_dict=True)
		self.assertTrue("run" in dir(query))
		self.assertIsInstance(query.run, Callable)
		self.assertIsInstance(data, list)

	def test_agg_funcs(self):
		kanivin.db.truncate("Communication")
		sample_data = {
			"doctype": "Communication",
			"communication_type": "Communication",
			"content": "testing",
			"rating": 1,
		}
		kanivin.get_doc(sample_data).insert()
		sample_data["rating"] = 3
		kanivin.get_doc(sample_data).insert()
		sample_data["rating"] = 4
		kanivin.get_doc(sample_data).insert()
		self.assertEqual(kanivin.qb.max("Communication", "rating"), 4)
		self.assertEqual(kanivin.qb.min("Communication", "rating"), 1)
		self.assertAlmostEqual(kanivin.qb.avg("Communication", "rating"), 2.666, places=2)
		self.assertEqual(kanivin.qb.sum("Communication", "rating"), 8.0)
		kanivin.db.rollback()


class TestParameterization(KanivinTestCase):
	def test_where_conditions(self):
		DocType = kanivin.qb.DocType("DocType")
		query = kanivin.qb.from_(DocType).select(DocType.name).where(DocType.owner == "Administrator' --")
		self.assertTrue("walk" in dir(query))
		query, params = query.walk()

		self.assertIn("%(param1)s", query)
		self.assertIn("param1", params)
		self.assertEqual(params["param1"], "Administrator' --")

	def test_set_conditions(self):
		DocType = kanivin.qb.DocType("DocType")
		query = kanivin.qb.update(DocType).set(DocType.value, "some_value")

		self.assertTrue("walk" in dir(query))
		query, params = query.walk()

		self.assertIn("%(param1)s", query)
		self.assertIn("param1", params)
		self.assertEqual(params["param1"], "some_value")

	def test_where_conditions_functions(self):
		DocType = kanivin.qb.DocType("DocType")
		query = (
			kanivin.qb.from_(DocType).select(DocType.name).where(Coalesce(DocType.search_fields == "subject"))
		)

		self.assertTrue("walk" in dir(query))
		query, params = query.walk()

		self.assertIn("%(param1)s", query)
		self.assertIn("param1", params)
		self.assertEqual(params["param1"], "subject")

	def test_case(self):
		DocType = kanivin.qb.DocType("DocType")
		query = kanivin.qb.from_(DocType).select(
			Case()
			.when(DocType.search_fields == "value", "other_value")
			.when(Coalesce(DocType.search_fields == "subject_in_function"), "true_value")
			.else_("Overdue")
		)

		self.assertTrue("walk" in dir(query))
		query, params = query.walk()

		self.assertIn("%(param1)s", query)
		self.assertIn("param1", params)
		self.assertEqual(params["param1"], "value")
		self.assertEqual(params["param2"], "other_value")
		self.assertEqual(params["param3"], "subject_in_function")
		self.assertEqual(params["param4"], "true_value")
		self.assertEqual(params["param5"], "Overdue")

	def test_case_in_update(self):
		DocType = kanivin.qb.DocType("DocType")
		query = kanivin.qb.update(DocType).set(
			"parent",
			Case()
			.when(DocType.search_fields == "value", "other_value")
			.when(Coalesce(DocType.search_fields == "subject_in_function"), "true_value")
			.else_("Overdue"),
		)

		self.assertTrue("walk" in dir(query))
		query, params = query.walk()

		self.assertIn("%(param1)s", query)
		self.assertIn("param1", params)
		self.assertEqual(params["param1"], "value")
		self.assertEqual(params["param2"], "other_value")
		self.assertEqual(params["param3"], "subject_in_function")
		self.assertEqual(params["param4"], "true_value")
		self.assertEqual(params["param5"], "Overdue")

	def test_named_parameter_wrapper(self):
		from kanivin.query_builder.terms import NamedParameterWrapper

		test_npw = NamedParameterWrapper()
		self.assertTrue(hasattr(test_npw, "parameters"))
		self.assertEqual(test_npw.get_sql("test_string_one"), "%(param1)s")
		self.assertEqual(test_npw.get_sql("test_string_two"), "%(param2)s")
		params = test_npw.get_parameters()
		for key in params.keys():
			# checks for param# format
			self.assertRegex(key, r"param\d")
		self.assertEqual(params["param1"], "test_string_one")


@run_only_if(db_type_is.MARIADB)
class TestBuilderMaria(KanivinTestCase, TestBuilderBase):
	def test_adding_tabs_in_from(self):
		self.assertEqual("SELECT * FROM `tabNotes`", kanivin.qb.from_("Notes").select("*").get_sql())
		self.assertEqual("SELECT * FROM `__Auth`", kanivin.qb.from_("__Auth").select("*").get_sql())

	def test_get_qb_type(self):
		from kanivin.query_builder import get_query_builder

		qb = get_query_builder(kanivin.db.db_type)
		self.assertEqual("SELECT * FROM `tabDocType`", qb().from_("DocType").select("*").get_sql())


@run_only_if(db_type_is.POSTGRES)
class TestBuilderPostgres(KanivinTestCase, TestBuilderBase):
	def test_adding_tabs_in_from(self):
		self.assertEqual('SELECT * FROM "tabNotes"', kanivin.qb.from_("Notes").select("*").get_sql())
		self.assertEqual('SELECT * FROM "__Auth"', kanivin.qb.from_("__Auth").select("*").get_sql())

	def test_replace_tables(self):
		info_schema = kanivin.qb.Schema("information_schema")
		self.assertEqual(
			'SELECT * FROM "pg_stat_all_tables"',
			kanivin.qb.from_(info_schema.tables).select("*").get_sql(),
		)

	def test_replace_fields_post(self):
		self.assertEqual("relname", kanivin.qb.Field("table_name").get_sql())

	def test_get_qb_type(self):
		from kanivin.query_builder import get_query_builder

		qb = get_query_builder(kanivin.db.db_type)
		self.assertEqual('SELECT * FROM "tabDocType"', qb().from_("DocType").select("*").get_sql())


class TestMisc(KanivinTestCase):
	def test_custom_func(self):
		rand_func = kanivin.qb.functions("rand", "45")
		self.assertIsInstance(rand_func, Function)
		self.assertEqual(rand_func.get_sql(), "rand('45')")

	def test_function_with_schema(self):
		from kanivin.query_builder import ParameterizedFunction

		x = ParameterizedFunction("rand", "45")
		x.schema = kanivin.qb.DocType("DocType")
		self.assertEqual("tabDocType.rand('45')", x.get_sql())

	def test_util_table(self):
		from kanivin.query_builder.utils import Table

		DocType = Table("DocType")
		self.assertEqual(DocType.get_sql(), "DocType")

	def test_union(self):
		user = kanivin.qb.DocType("User")
		role = kanivin.qb.DocType("Role")
		users = kanivin.qb.from_(user).select(user.name)
		roles = kanivin.qb.from_(role).select(role.name)

		self.assertEqual(set(users.run() + roles.run()), set((users + roles).run()))
