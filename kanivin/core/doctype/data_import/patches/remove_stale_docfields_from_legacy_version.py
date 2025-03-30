import kanivin


def execute():
	"""Remove stale docfields from legacy version"""
	kanivin.db.delete("DocField", {"options": "Data Import", "parent": "Data Import Legacy"})
