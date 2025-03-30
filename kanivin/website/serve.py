from werkzeug.wrappers import Response

import kanivin
from kanivin.permissions import handle_does_not_exist_error
from kanivin.website.page_renderers.error_page import ErrorPage
from kanivin.website.page_renderers.not_found_page import NotFoundPage
from kanivin.website.page_renderers.not_permitted_page import NotPermittedPage
from kanivin.website.page_renderers.redirect_page import RedirectPage
from kanivin.website.path_resolver import PathResolver


def get_response(path=None, http_status_code=200) -> Response:
	"""Resolves path and renders page"""
	path = path or kanivin.local.request.path
	endpoint = path

	try:
		path_resolver = PathResolver(path, http_status_code)
		endpoint, renderer_instance = path_resolver.resolve()
		return renderer_instance.render()

	except Exception as e:
		return handle_exception(e, endpoint, path, http_status_code)


@handle_does_not_exist_error
def handle_exception(e, endpoint, path, http_status_code):
	if isinstance(e, kanivin.Redirect):
		return RedirectPage(endpoint or path, e.http_status_code).render()

	if isinstance(e, kanivin.PermissionError):
		return NotPermittedPage(endpoint, http_status_code, exception=e).render()

	if isinstance(e, kanivin.PageDoesNotExistError):
		return NotFoundPage(endpoint, http_status_code).render()

	return ErrorPage(exception=e).render()


def get_response_content(path=None, http_status_code=200) -> str:
	response = get_response(path, http_status_code)
	return str(response.data, "utf-8")


def get_response_without_exception_handling(path=None, http_status_code=200) -> Response:
	"""Resolves path and renders page.

	Note: This doesn't do any exception handling and assumes you'll implement the exception
	handling that's required."""
	path = path or kanivin.local.request.path

	path_resolver = PathResolver(path, http_status_code)
	_endpoint, renderer_instance = path_resolver.resolve()
	return renderer_instance.render()
