kanivin.pages["user-profile"].on_page_load = function (wrapper) {
	kanivin.require("user_profile_controller.bundle.js", () => {
		let user_profile = new kanivin.ui.UserProfile(wrapper);
		user_profile.show();
	});
};
