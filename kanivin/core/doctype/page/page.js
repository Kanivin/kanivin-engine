// Copyright (c) 2016, Kanivin and contributors
// For license information, please see license.txt

kanivin.ui.form.on("Page", {
	refresh: function (frm) {
		if (!kanivin.boot.developer_mode && kanivin.session.user != "Administrator") {
			// make the document read-only
			frm.set_read_only();
		}
		if (!frm.is_new() && !frm.doc.istable) {
			frm.add_custom_button(__("Go to {0} Page", [frm.doc.title || frm.doc.name]), () => {
				kanivin.set_route(frm.doc.name);
			});
		}
	},
});
