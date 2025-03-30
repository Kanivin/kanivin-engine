# Copyright (c) 2021, Kanivin Technologies Pvt. Ltd. and Contributors
# MIT License. See LICENSE

from frappe.exceptions import ValidationError


class NewsletterAlreadySentError(ValidationError):
	pass


class NoRecipientFoundError(ValidationError):
	pass


class NewsletterNotSavedError(ValidationError):
	pass
