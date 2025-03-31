// Copyright (c) 2019, Kanivin Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Google Settings", {
	refresh: function (frm) {
		frm.dashboard.set_headline(
			__("For more information, {0}.", [
				`<a href='https://kanierp.com/docs/user/manual/en/kanierp_integration/google_settings'>${__(
					"Click here"
				)}</a>`,
			])
		);
	},
});
