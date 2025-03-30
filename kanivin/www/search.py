import markupsafe

import kanivin
from kanivin import _
from kanivin.core.utils import html2text
from kanivin.utils import sanitize_html
from kanivin.utils.global_search import web_search


def get_context(context):
	context.no_cache = 1
	if kanivin.form_dict.q:
		query = str(markupsafe.escape(sanitize_html(kanivin.form_dict.q)))
		context.title = _("Search Results for")
		context.query = query
		context.route = "/search"
		context.update(get_search_results(query, kanivin.utils.sanitize_html(kanivin.form_dict.scope)))
	else:
		context.title = _("Search")


@kanivin.whitelist(allow_guest=True)
def get_search_results(text: str, scope: str | None = None, start: int = 0, as_html: bool = False):
	results = web_search(text, scope, start, limit=21)
	out = kanivin._dict()

	if len(results) == 21:
		out.has_more = 1
		results = results[:20]

	for d in results:
		try:
			d.content = html2text(d.content)
			index = d.content.lower().index(text.lower())
			d.content = (
				d.content[:index]
				+ "<mark>"
				+ d.content[index:][: len(text)]
				+ "</mark>"
				+ d.content[index + len(text) :]
			)

			if index < 40:
				start = 0
				prefix = ""
			else:
				start = index - 40
				prefix = "..."

			suffix = ""
			if (index + len(text) + 47) < len(d.content):
				suffix = "..."

			d.preview = prefix + d.content[start : start + len(text) + 87] + suffix
		except Exception:
			d.preview = html2text(d.content)[:97] + "..."

	out.results = results

	if as_html:
		out.results = kanivin.render_template("templates/includes/search_result.html", out)

	return out
