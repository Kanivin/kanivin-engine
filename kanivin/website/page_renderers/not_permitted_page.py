from urllib.parse import quote_plus

import kanivin
from kanivin import _
from kanivin.utils import cstr
from kanivin.website.page_renderers.template_page import TemplatePage


class NotPermittedPage(TemplatePage):
	def __init__(self, path=None, http_status_code=None, exception=""):
		kanivin.local.message = cstr(exception)
		super().__init__(path=path, http_status_code=http_status_code)
		self.http_status_code = 403

	def can_render(self):
		return True

	def render(self):
		action = f"/login?redirect-to={quote_plus(kanivin.request.path)}"
		if kanivin.request.path.startswith("/app/") or kanivin.request.path == "/app":
			action = "/login"
		kanivin.local.message_title = _("Not Permitted")
		kanivin.local.response["context"] = dict(
			indicator_color="red", primary_action=action, primary_label=_("Login"), fullpage=True
		)
		self.set_standard_path("message")
		return super().render()
