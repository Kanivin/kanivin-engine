// Copyright (c) 2020, Kanivin and contributors
// For license information, please see license.txt

kanivin.ui.form.on("Navbar Settings", {
	after_save: function (frm) {
		kanivin.ui.toolbar.clear_cache();
	},
});
