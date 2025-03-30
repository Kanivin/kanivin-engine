import kanivin


def execute():
	kanivin.reload_doctype("Translation")
	kanivin.db.sql(
		"UPDATE `tabTranslation` SET `translated_text`=`target_name`, `source_text`=`source_name`, `contributed`=0"
	)
