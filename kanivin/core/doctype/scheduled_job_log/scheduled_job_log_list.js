kanivin.listview_settings["Scheduled Job Log"] = {
	onload: function (listview) {
		kanivin.require("logtypes.bundle.js", () => {
			kanivin.utils.logtypes.show_log_retention_message(cur_list.doctype);
		});
	},
};
