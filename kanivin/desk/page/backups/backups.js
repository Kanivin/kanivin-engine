kanivin.pages["backups"].on_page_load = function (wrapper) {
	var page = kanivin.ui.make_app_page({
		parent: wrapper,
		title: __("Download Backups"),
		single_column: true,
	});

	page.add_inner_button(__("Set Number of Backups"), function () {
		kanivin.set_route("Form", "System Settings");
	});

	page.add_inner_button(__("Download Files Backup"), function () {
		kanivin.call({
			method: "kanivin.desk.page.backups.backups.schedule_files_backup",
			args: { user_email: kanivin.session.user_email },
		});
	});

	page.add_inner_button(__("Get Backup Encryption Key"), function () {
		if (kanivin.user.has_role("System Manager")) {
			kanivin.verify_password(function () {
				kanivin.call({
					method: "kanivin.utils.backups.get_backup_encryption_key",
					callback: function (r) {
						kanivin.msgprint({
							title: __("Backup Encryption Key"),
							message: __(r.message),
							indicator: "blue",
						});
					},
				});
			});
		} else {
			kanivin.msgprint({
				title: __("Error"),
				message: __("System Manager privileges required."),
				indicator: "red",
			});
		}
	});

	kanivin.breadcrumbs.add("Setup");

	$(kanivin.render_template("backups")).appendTo(page.body.addClass("no-border"));
};
