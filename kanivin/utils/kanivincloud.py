import kanivin

FRAPPE_CLOUD_DOMAINS = ("kanivin.cloud", "erpnext.com", "kanivinhr.com", "kanivin.dev")


def on_kanivincloud() -> bool:
	"""Returns true if running on Kanivin Cloud.


	Useful for modifying few features for better UX."""
	return kanivin.local.site.endswith(FRAPPE_CLOUD_DOMAINS)
