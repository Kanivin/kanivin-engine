import kanivin
from kanivin.cache_manager import clear_defaults_cache


def execute():
	kanivin.db.set_default(
		"suspend_email_queue",
		kanivin.db.get_default("hold_queue", "Administrator") or 0,
		parent="__default",
	)

	kanivin.db.delete("DefaultValue", {"defkey": "hold_queue"})
	clear_defaults_cache()
