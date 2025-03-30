kanivin.user_info = function (uid) {
	if (!uid) uid = kanivin.session.user;

	let user_info;
	if (!(kanivin.boot.user_info && kanivin.boot.user_info[uid])) {
		user_info = { fullname: uid || "Unknown" };
	} else {
		user_info = kanivin.boot.user_info[uid];
	}

	user_info.abbr = kanivin.get_abbr(user_info.fullname);
	user_info.color = kanivin.get_palette(user_info.fullname);

	return user_info;
};

kanivin.update_user_info = function (user_info) {
	for (let user in user_info) {
		if (kanivin.boot.user_info[user]) {
			Object.assign(kanivin.boot.user_info[user], user_info[user]);
		} else {
			kanivin.boot.user_info[user] = user_info[user];
		}
	}
};

kanivin.provide("kanivin.user");

$.extend(kanivin.user, {
	name: "Guest",
	full_name: function (uid) {
		return uid === kanivin.session.user
			? __(
					"You",
					null,
					"Name of the current user. For example: You edited this 5 hours ago."
			  )
			: kanivin.user_info(uid).fullname;
	},
	image: function (uid) {
		return kanivin.user_info(uid).image;
	},
	abbr: function (uid) {
		return kanivin.user_info(uid).abbr;
	},
	has_role: function (rl) {
		if (typeof rl == "string") rl = [rl];
		for (var i in rl) {
			if ((kanivin.boot ? kanivin.boot.user.roles : ["Guest"]).indexOf(rl[i]) != -1)
				return true;
		}
	},
	get_desktop_items: function () {
		// hide based on permission
		var modules_list = $.map(kanivin.boot.allowed_modules, function (icon) {
			var m = icon.module_name;
			var type = kanivin.modules[m] && kanivin.modules[m].type;

			if (kanivin.boot.user.allow_modules.indexOf(m) === -1) return null;

			var ret = null;
			if (type === "module") {
				if (kanivin.boot.user.allow_modules.indexOf(m) != -1 || kanivin.modules[m].is_help)
					ret = m;
			} else if (type === "page") {
				if (kanivin.boot.allowed_pages.indexOf(kanivin.modules[m].link) != -1) ret = m;
			} else if (type === "list") {
				if (kanivin.model.can_read(kanivin.modules[m]._doctype)) ret = m;
			} else if (type === "view") {
				ret = m;
			} else if (type === "setup") {
				if (
					kanivin.user.has_role("System Manager") ||
					kanivin.user.has_role("Administrator")
				)
					ret = m;
			} else {
				ret = m;
			}

			return ret;
		});

		return modules_list;
	},

	is_report_manager: function () {
		return kanivin.user.has_role(["Administrator", "System Manager", "Report Manager"]);
	},

	get_formatted_email: function (email) {
		var fullname = kanivin.user.full_name(email);

		if (!fullname) {
			return email;
		} else {
			// to quote or to not
			var quote = "";

			// only if these special characters are found
			// why? To make the output same as that in python!
			if (fullname.search(/[\[\]\\()<>@,:;".]/) !== -1) {
				quote = '"';
			}

			return repl("%(quote)s%(fullname)s%(quote)s <%(email)s>", {
				fullname: fullname,
				email: email,
				quote: quote,
			});
		}
	},

	get_emails: () => {
		return Object.keys(kanivin.boot.user_info).map((key) => kanivin.boot.user_info[key].email);
	},

	/* Normally kanivin.user is an object
	 * having properties and methods.
	 * But in the following case
	 *
	 * if (kanivin.user === 'Administrator')
	 *
	 * kanivin.user will cast to a string
	 * returning kanivin.user.name
	 */
	toString: function () {
		return this.name;
	},
});

kanivin.session_alive = true;
$(document).bind("mousemove", function () {
	if (kanivin.session_alive === false) {
		$(document).trigger("session_alive");
	}
	kanivin.session_alive = true;
	if (kanivin.session_alive_timeout) clearTimeout(kanivin.session_alive_timeout);
	kanivin.session_alive_timeout = setTimeout("kanivin.session_alive=false;", 30000);
});
