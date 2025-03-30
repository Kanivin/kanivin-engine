import kanivin


def execute():
	kanivin.reload_doc("website", "doctype", "website_theme_ignore_app")
	kanivin.reload_doc("website", "doctype", "color")
	kanivin.reload_doc("website", "doctype", "website_theme", force=True)

	for theme in kanivin.get_all("Website Theme"):
		doc = kanivin.get_doc("Website Theme", theme.name)
		setup_color_record(doc)
		if not doc.get("custom_scss") and doc.theme_scss:
			# move old theme to new theme
			doc.custom_scss = doc.theme_scss
			doc.save()


def setup_color_record(doc):
	color_fields = [
		"primary_color",
		"text_color",
		"light_color",
		"dark_color",
		"background_color",
	]

	for color_field in color_fields:
		color_code = doc.get(color_field)
		if not color_code or kanivin.db.exists("Color", color_code):
			continue

		kanivin.get_doc(
			{
				"doctype": "Color",
				"__newname": color_code,
				"color": color_code,
			}
		).insert()
