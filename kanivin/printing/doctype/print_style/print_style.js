// Copyright (c) 2017, Kanivin and contributors
// For license information, please see license.txt

kanivin.ui.form.on("Print Style", {
	refresh: function (frm) {
		frm.add_custom_button(__("Print Settings"), () => {
			kanivin.set_route("Form", "Print Settings");
		});
	},
});
