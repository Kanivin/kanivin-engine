import os

import kanivin
from kanivin.database.db_manager import DbManager
from kanivin.utils import cint


def setup_database():
	root_conn = get_root_connection(kanivin.flags.root_login, kanivin.flags.root_password)
	root_conn.commit()
	root_conn.sql("end")
	root_conn.sql(f'DROP DATABASE IF EXISTS "{kanivin.conf.db_name}"')

	# If user exists, just update password
	if root_conn.sql(f"SELECT 1 FROM pg_roles WHERE rolname='{kanivin.conf.db_name}'"):
		root_conn.sql(f"ALTER USER \"{kanivin.conf.db_name}\" WITH PASSWORD '{kanivin.conf.db_password}'")
	else:
		root_conn.sql(f"CREATE USER \"{kanivin.conf.db_name}\" WITH PASSWORD '{kanivin.conf.db_password}'")
	root_conn.sql(f'CREATE DATABASE "{kanivin.conf.db_name}"')
	root_conn.sql(f'GRANT ALL PRIVILEGES ON DATABASE "{kanivin.conf.db_name}" TO "{kanivin.conf.db_name}"')
	if psql_version := root_conn.sql("SHOW server_version_num", as_dict=True):
		semver_version_num = psql_version[0].get("server_version_num") or "140000"
		if cint(semver_version_num) > 150000:
			root_conn.sql(f'ALTER DATABASE "{kanivin.conf.db_name}" OWNER TO "{kanivin.conf.db_name}"')
	root_conn.close()


def bootstrap_database(verbose, source_sql=None):
	kanivin.connect()
	import_db_from_sql(source_sql, verbose)
	kanivin.connect()

	if "tabDefaultValue" not in kanivin.db.get_tables():
		import sys

		from click import secho

		secho(
			"Table 'tabDefaultValue' missing in the restored site. "
			"This happens when the backup fails to restore. Please check that the file is valid\n"
			"Do go through the above output to check the exact error message from MariaDB",
			fg="red",
		)
		sys.exit(1)


def import_db_from_sql(source_sql=None, verbose=False):
	if verbose:
		print("Starting database import...")
	db_name = kanivin.conf.db_name
	if not source_sql:
		source_sql = os.path.join(os.path.dirname(__file__), "framework_postgres.sql")
	DbManager(kanivin.local.db).restore_database(
		verbose, db_name, source_sql, db_name, kanivin.conf.db_password
	)
	if verbose:
		print("Imported from database %s" % source_sql)


def get_root_connection(root_login=None, root_password=None):
	if not kanivin.local.flags.root_connection:
		if not root_login:
			root_login = kanivin.conf.get("root_login") or None

		if not root_login:
			root_login = input("Enter postgres super user: ")

		if not root_password:
			root_password = kanivin.conf.get("root_password") or None

		if not root_password:
			from getpass import getpass

			root_password = getpass("Postgres super user password: ")

		kanivin.local.flags.root_connection = kanivin.database.get_db(
			socket=kanivin.conf.db_socket,
			host=kanivin.conf.db_host,
			port=kanivin.conf.db_port,
			user=root_login,
			password=root_password,
			cur_db_name=root_login,
		)

	return kanivin.local.flags.root_connection


def drop_user_and_database(db_name, root_login, root_password):
	root_conn = get_root_connection(
		kanivin.flags.root_login or root_login, kanivin.flags.root_password or root_password
	)
	root_conn.commit()
	root_conn.sql(
		"SELECT pg_terminate_backend (pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = %s",
		(db_name,),
	)
	root_conn.sql("end")
	root_conn.sql(f"DROP DATABASE IF EXISTS {db_name}")
	root_conn.sql(f"DROP USER IF EXISTS {db_name}")
