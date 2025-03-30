import kanivin
from kanivin.utils import cint

no_cache = 1


def get_context(context):
	kanivin.db.commit()  # nosemgrep
	context = kanivin._dict()
	context.boot = get_boot()
	return context


def get_boot():
	return kanivin._dict(
		{
			"site_name": kanivin.local.site,
			"read_only_mode": kanivin.flags.read_only,
			"csrf_token": kanivin.sessions.get_csrf_token(),
			"setup_complete": cint(kanivin.get_system_settings("setup_complete")),
		}
	)
