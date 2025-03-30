"""
Run this after updating country_info.json and or
"""
import kanivin


def execute():
	for col in ("field", "doctype"):
		kanivin.db.sql_ddl(f"alter table `tabSingles` modify column `{col}` varchar(255)")
