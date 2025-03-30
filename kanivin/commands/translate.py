import click

from kanivin.commands import get_site, pass_context
from kanivin.exceptions import SiteNotSpecifiedError


# translation
@click.command("build-message-files")
@pass_context
def build_message_files(context):
	"Build message files for translation"
	import kanivin.translate

	for site in context.sites:
		try:
			kanivin.init(site=site)
			kanivin.connect()
			kanivin.translate.rebuild_all_translation_files()
		finally:
			kanivin.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError


@click.command("new-language")  # , help="Create lang-code.csv for given app")
@pass_context
@click.argument("lang_code")  # , help="Language code eg. en")
@click.argument("app")  # , help="App name eg. kanivin")
def new_language(context, lang_code, app):
	"""Create lang-code.csv for given app"""
	import kanivin.translate

	if not context["sites"]:
		raise Exception("--site is required")

	# init site
	kanivin.init(site=context["sites"][0])
	kanivin.connect()
	kanivin.translate.write_translations_file(app, lang_code)

	print(f"File created at ./apps/{app}/{app}/translations/{lang_code}.csv")
	print("You will need to add the language in kanivin/geo/languages.json, if you haven't done it already.")


@click.command("get-untranslated")
@click.option("--app", default="_ALL_APPS")
@click.argument("lang")
@click.argument("untranslated_file")
@click.option("--all", default=False, is_flag=True, help="Get all message strings")
@pass_context
def get_untranslated(context, lang, untranslated_file, app="_ALL_APPS", all=None):
	"Get untranslated strings for language"
	import kanivin.translate

	site = get_site(context)
	try:
		kanivin.init(site=site)
		kanivin.connect()
		kanivin.translate.get_untranslated(lang, untranslated_file, get_all=all, app=app)
	finally:
		kanivin.destroy()


@click.command("update-translations")
@click.option("--app", default="_ALL_APPS")
@click.argument("lang")
@click.argument("untranslated_file")
@click.argument("translated-file")
@pass_context
def update_translations(context, lang, untranslated_file, translated_file, app="_ALL_APPS"):
	"Update translated strings"
	import kanivin.translate

	site = get_site(context)
	try:
		kanivin.init(site=site)
		kanivin.connect()
		kanivin.translate.update_translations(lang, untranslated_file, translated_file, app=app)
	finally:
		kanivin.destroy()


@click.command("import-translations")
@click.argument("lang")
@click.argument("path")
@pass_context
def import_translations(context, lang, path):
	"Update translated strings"
	import kanivin.translate

	site = get_site(context)
	try:
		kanivin.init(site=site)
		kanivin.connect()
		kanivin.translate.import_translations(lang, path)
	finally:
		kanivin.destroy()


@click.command("migrate-translations")
@click.argument("source-app")
@click.argument("target-app")
@pass_context
def migrate_translations(context, source_app, target_app):
	"Migrate target-app-specific translations from source-app to target-app"
	import kanivin.translate

	site = get_site(context)
	try:
		kanivin.init(site=site)
		kanivin.connect()
		kanivin.translate.migrate_translations(source_app, target_app)
	finally:
		kanivin.destroy()


commands = [
	build_message_files,
	get_untranslated,
	import_translations,
	new_language,
	update_translations,
	migrate_translations,
]
