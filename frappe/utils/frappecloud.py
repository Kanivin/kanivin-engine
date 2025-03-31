import frappe

FRAPPE_CLOUD_DOMAINS = ("frappe.cloud", "kanierp.com", "frappehr.com", "frappe.dev")


def on_frappecloud() -> bool:
	"""Returns true if running on Kanivin Cloud.


	Useful for modifying few features for better UX."""
	return frappe.local.site.endswith(FRAPPE_CLOUD_DOMAINS)
