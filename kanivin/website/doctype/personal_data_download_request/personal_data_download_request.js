// Copyright (c) 2019, Kanivin and contributors
// For license information, please see license.txt

kanivin.ui.form.on("Personal Data Download Request", {
	onload: function (frm) {
		if (frm.is_new()) {
			frm.doc.user = kanivin.session.user;
		}
	},
});
