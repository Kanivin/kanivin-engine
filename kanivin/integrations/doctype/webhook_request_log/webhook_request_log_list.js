kanivin.listview_settings["Webhook Request Log"] = {
	onload: function (list_view) {
		kanivin.require("logtypes.bundle.js", () => {
			kanivin.utils.logtypes.show_log_retention_message(list_view.doctype);
		});
	},
};
