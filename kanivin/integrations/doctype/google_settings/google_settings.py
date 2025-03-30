# Copyright (c) 2019, Kanivin and contributors
# License: MIT. See LICENSE

import 
from .model.document import Document


class GoogleSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from .types import DF

		api_key: DF.Data | None
		app_id: DF.Data | None
		client_id: DF.Data | None
		client_secret: DF.Password | None
		enable: DF.Check
		google_drive_picker_enabled: DF.Check
	# end: auto-generated types

	pass


@.whitelist()
def get_file_picker_settings():
	"""Return all the data FileUploader needs to start the Google Drive Picker."""
	google_settings = .get_cached_doc("Google Settings")

	if not (google_settings.enable and google_settings.google_drive_picker_enabled):
		return {}

	return {
		"enabled": True,
		"appId": google_settings.app_id,
		"clientId": google_settings.client_id,
	}
