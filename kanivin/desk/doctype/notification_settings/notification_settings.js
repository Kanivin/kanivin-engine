// Copyright (c) 2019, Kanivin and contributors
// For license information, please see license.txt

kanivin.ui.form.on("Notification Settings", {
	onload: (frm) => {
		frm.set_query("subscribed_documents", () => {
			return {
				filters: {
					istable: 0,
				},
			};
		});
	},

	refresh: (frm) => {
		if (kanivin.user.has_role("System Manager")) {
			frm.add_custom_button(__("Go to Notification Settings List"), () => {
				kanivin.set_route("List", "Notification Settings");
			});
		}
	},
});
