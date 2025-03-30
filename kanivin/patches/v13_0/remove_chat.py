import click

import kanivin


def execute():
	kanivin.delete_doc_if_exists("DocType", "Chat Message")
	kanivin.delete_doc_if_exists("DocType", "Chat Message Attachment")
	kanivin.delete_doc_if_exists("DocType", "Chat Profile")
	kanivin.delete_doc_if_exists("DocType", "Chat Token")
	kanivin.delete_doc_if_exists("DocType", "Chat Room User")
	kanivin.delete_doc_if_exists("DocType", "Chat Room")
	kanivin.delete_doc_if_exists("Module Def", "Chat")

	click.secho(
		"Chat Module is moved to a separate app and is removed from Kanivin in version-13.\n"
		"Please install the app to continue using the chat feature: https://github.com/kanivin/chat",
		fg="yellow",
	)
