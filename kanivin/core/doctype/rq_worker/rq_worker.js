// Copyright (c) 2025, Kanivin and contributors
// For license information, please see license.txt

kanivin.ui.form.on("RQ Worker", {
	refresh: function (frm) {
		// Nothing in this form is supposed to be editable.
		frm.disable_form();
	},
});
