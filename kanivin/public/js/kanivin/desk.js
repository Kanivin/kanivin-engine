// Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
// MIT License. See license.txt
/* eslint-disable no-console */

// __('Modules') __('Domains') __('Places') __('Administration') # for translation, don't remove

kanivin.start_app = function () {
	if (!kanivin.Application) return;
	kanivin.assets.check();
	kanivin.provide("kanivin.app");
	kanivin.provide("kanivin.desk");
	kanivin.app = new kanivin.Application();
};

$(document).ready(function () {
	if (!kanivin.utils.supportsES6) {
		kanivin.msgprint({
			indicator: "red",
			title: __("Browser not supported"),
			message: __(
				"Some of the features might not work in your browser. Please update your browser to the latest version."
			),
		});
	}
	kanivin.start_app();
});

kanivin.Application = class Application {
	constructor() {
		this.startup();
	}

	startup() {
		kanivin.realtime.init();
		kanivin.model.init();

		this.load_bootinfo();
		this.load_user_permissions();
		this.make_nav_bar();
		this.set_favicon();
		this.set_fullwidth_if_enabled();
		this.add_browser_class();
		this.setup_energy_point_listeners();
		this.setup_copy_doc_listener();
		this.setup_broadcast_listeners();

		kanivin.ui.keys.setup();

		kanivin.ui.keys.add_shortcut({
			shortcut: "shift+ctrl+g",
			description: __("Switch Theme"),
			action: () => {
				if (kanivin.theme_switcher && kanivin.theme_switcher.dialog.is_visible) {
					kanivin.theme_switcher.hide();
				} else {
					kanivin.theme_switcher = new kanivin.ui.ThemeSwitcher();
					kanivin.theme_switcher.show();
				}
			},
		});

		kanivin.ui.add_system_theme_switch_listener();
		const root = document.documentElement;

		const observer = new MutationObserver(() => {
			kanivin.ui.set_theme();
		});
		observer.observe(root, {
			attributes: true,
			attributeFilter: ["data-theme-mode"],
		});

		kanivin.ui.set_theme();

		// page container
		this.make_page_container();
		if (
			!window.Cypress &&
			kanivin.boot.onboarding_tours &&
			kanivin.boot.user.onboarding_status != null
		) {
			let pending_tours = !kanivin.boot.onboarding_tours.every(
				(tour) => kanivin.boot.user.onboarding_status[tour[0]]?.is_complete
			);
			if (pending_tours && kanivin.boot.onboarding_tours.length > 0) {
				kanivin.require("onboarding_tours.bundle.js", () => {
					kanivin.utils.sleep(1000).then(() => {
						kanivin.ui.init_onboarding_tour();
					});
				});
			}
		}
		this.set_route();

		// trigger app startup
		$(document).trigger("startup");

		$(document).trigger("app_ready");

		if (kanivin.boot.messages) {
			kanivin.msgprint(kanivin.boot.messages);
		}

		if (kanivin.user_roles.includes("System Manager")) {
			// delayed following requests to make boot faster
			setTimeout(() => {
				this.show_change_log();
				this.show_update_available();
			}, 1000);
		}

		if (!kanivin.boot.developer_mode) {
			let console_security_message = __(
				"Using this console may allow attackers to impersonate you and steal your information. Do not enter or paste code that you do not understand."
			);
			console.log(`%c${console_security_message}`, "font-size: large");
		}

		this.show_notes();

		if (kanivin.ui.startup_setup_dialog && !kanivin.boot.setup_complete) {
			kanivin.ui.startup_setup_dialog.pre_show();
			kanivin.ui.startup_setup_dialog.show();
		}

		kanivin.realtime.on("version-update", function () {
			var dialog = kanivin.msgprint({
				message: __(
					"The application has been updated to a new version, please refresh this page"
				),
				indicator: "green",
				title: __("Version Updated"),
			});
			dialog.set_primary_action(__("Refresh"), function () {
				location.reload(true);
			});
			dialog.get_close_btn().toggle(false);
		});

		// listen to build errors
		this.setup_build_events();

		if (kanivin.sys_defaults.email_user_password) {
			var email_list = kanivin.sys_defaults.email_user_password.split(",");
			for (var u in email_list) {
				if (email_list[u] === kanivin.user.name) {
					this.set_password(email_list[u]);
				}
			}
		}

		// REDESIGN-TODO: Fix preview popovers
		this.link_preview = new kanivin.ui.LinkPreview();

		kanivin.broadcast.emit("boot", {
			csrf_token: kanivin.csrf_token,
			user: kanivin.session.user,
		});
	}

	set_route() {
		if (kanivin.boot && localStorage.getItem("session_last_route")) {
			kanivin.set_route(localStorage.getItem("session_last_route"));
			localStorage.removeItem("session_last_route");
		} else {
			// route to home page
			kanivin.router.route();
		}
		kanivin.router.on("change", () => {
			$(".tooltip").hide();
		});
	}

	set_password(user) {
		var me = this;
		kanivin.call({
			method: "kanivin.core.doctype.user.user.get_email_awaiting",
			args: {
				user: user,
			},
			callback: function (email_account) {
				email_account = email_account["message"];
				if (email_account) {
					var i = 0;
					if (i < email_account.length) {
						me.email_password_prompt(email_account, user, i);
					}
				}
			},
		});
	}

	email_password_prompt(email_account, user, i) {
		var me = this;
		const email_id = email_account[i]["email_id"];
		let d = new kanivin.ui.Dialog({
			title: __("Password missing in Email Account"),
			fields: [
				{
					fieldname: "password",
					fieldtype: "Password",
					label: __(
						"Please enter the password for: <b>{0}</b>",
						[email_id],
						"Email Account"
					),
					reqd: 1,
				},
				{
					fieldname: "submit",
					fieldtype: "Button",
					label: __("Submit", null, "Submit password for Email Account"),
				},
			],
		});
		d.get_input("submit").on("click", function () {
			//setup spinner
			d.hide();
			var s = new kanivin.ui.Dialog({
				title: __("Checking one moment"),
				fields: [
					{
						fieldtype: "HTML",
						fieldname: "checking",
					},
				],
			});
			s.fields_dict.checking.$wrapper.html('<i class="fa fa-spinner fa-spin fa-4x"></i>');
			s.show();
			kanivin.call({
				method: "kanivin.email.doctype.email_account.email_account.set_email_password",
				args: {
					email_account: email_account[i]["email_account"],
					password: d.get_value("password"),
				},
				callback: function (passed) {
					s.hide();
					d.hide(); //hide waiting indication
					if (!passed["message"]) {
						kanivin.show_alert(
							{ message: __("Login Failed please try again"), indicator: "error" },
							5
						);
						me.email_password_prompt(email_account, user, i);
					} else {
						if (i + 1 < email_account.length) {
							i = i + 1;
							me.email_password_prompt(email_account, user, i);
						}
					}
				},
			});
		});
		d.show();
	}
	load_bootinfo() {
		if (kanivin.boot) {
			this.setup_workspaces();
			kanivin.model.sync(kanivin.boot.docs);
			this.check_metadata_cache_status();
			this.set_globals();
			this.sync_pages();
			kanivin.router.setup();
			this.setup_moment();
			if (kanivin.boot.print_css) {
				kanivin.dom.set_style(kanivin.boot.print_css, "print-style");
			}
			kanivin.user.name = kanivin.boot.user.name;
			kanivin.router.setup();
		} else {
			this.set_as_guest();
		}
	}

	setup_workspaces() {
		kanivin.modules = {};
		kanivin.workspaces = {};
		for (let page of kanivin.boot.allowed_workspaces || []) {
			kanivin.modules[page.module] = page;
			kanivin.workspaces[kanivin.router.slug(page.name)] = page;
		}
	}

	load_user_permissions() {
		kanivin.defaults.load_user_permission_from_boot();

		kanivin.realtime.on(
			"update_user_permissions",
			kanivin.utils.debounce(() => {
				kanivin.defaults.update_user_permissions();
			}, 500)
		);
	}

	check_metadata_cache_status() {
		if (kanivin.boot.metadata_version != localStorage.metadata_version) {
			kanivin.assets.clear_local_storage();
			kanivin.assets.init_local_storage();
		}
	}

	set_globals() {
		kanivin.session.user = kanivin.boot.user.name;
		kanivin.session.logged_in_user = kanivin.boot.user.name;
		kanivin.session.user_email = kanivin.boot.user.email;
		kanivin.session.user_fullname = kanivin.user_info().fullname;

		kanivin.user_defaults = kanivin.boot.user.defaults;
		kanivin.user_roles = kanivin.boot.user.roles;
		kanivin.sys_defaults = kanivin.boot.sysdefaults;

		kanivin.ui.py_date_format = kanivin.boot.sysdefaults.date_format
			.replace("dd", "%d")
			.replace("mm", "%m")
			.replace("yyyy", "%Y");
		kanivin.boot.user.last_selected_values = {};
	}
	sync_pages() {
		// clear cached pages if timestamp is not found
		if (localStorage["page_info"]) {
			kanivin.boot.allowed_pages = [];
			var page_info = JSON.parse(localStorage["page_info"]);
			$.each(kanivin.boot.page_info, function (name, p) {
				if (!page_info[name] || page_info[name].modified != p.modified) {
					delete localStorage["_page:" + name];
				}
				kanivin.boot.allowed_pages.push(name);
			});
		} else {
			kanivin.boot.allowed_pages = Object.keys(kanivin.boot.page_info);
		}
		localStorage["page_info"] = JSON.stringify(kanivin.boot.page_info);
	}
	set_as_guest() {
		kanivin.session.user = "Guest";
		kanivin.session.user_email = "";
		kanivin.session.user_fullname = "Guest";

		kanivin.user_defaults = {};
		kanivin.user_roles = ["Guest"];
		kanivin.sys_defaults = {};
	}
	make_page_container() {
		if ($("#body").length) {
			$(".splash").remove();
			kanivin.temp_container = $("<div id='temp-container' style='display: none;'>").appendTo(
				"body"
			);
			kanivin.container = new kanivin.views.Container();
		}
	}
	make_nav_bar() {
		// toolbar
		if (kanivin.boot && kanivin.boot.home_page !== "setup-wizard") {
			kanivin.kanivin_toolbar = new kanivin.ui.toolbar.Toolbar();
		}
	}
	logout() {
		var me = this;
		me.logged_out = true;
		return kanivin.call({
			method: "logout",
			callback: function (r) {
				if (r.exc) {
					return;
				}
				me.redirect_to_login();
			},
		});
	}
	handle_session_expired() {
		kanivin.app.redirect_to_login();
	}
	redirect_to_login() {
		window.location.href = `/login?redirect-to=${encodeURIComponent(
			window.location.pathname + window.location.search
		)}`;
	}
	set_favicon() {
		var link = $('link[type="image/x-icon"]').remove().attr("href");
		$('<link rel="shortcut icon" href="' + link + '" type="image/x-icon">').appendTo("head");
		$('<link rel="icon" href="' + link + '" type="image/x-icon">').appendTo("head");
	}
	trigger_primary_action() {
		// to trigger change event on active input before triggering primary action
		$(document.activeElement).blur();
		// wait for possible JS validations triggered after blur (it might change primary button)
		setTimeout(() => {
			if (window.cur_dialog && cur_dialog.display && !cur_dialog.is_minimized) {
				// trigger primary
				cur_dialog.get_primary_btn().trigger("click");
			} else if (cur_frm && cur_frm.page.btn_primary.is(":visible")) {
				cur_frm.page.btn_primary.trigger("click");
			} else if (kanivin.container.page.save_action) {
				kanivin.container.page.save_action();
			}
		}, 100);
	}

	show_change_log() {
		var me = this;
		let change_log = kanivin.boot.change_log;

		// kanivin.boot.change_log = [{
		// 	"change_log": [
		// 		[<version>, <change_log in markdown>],
		// 		[<version>, <change_log in markdown>],
		// 	],
		// 	"description": "ERP made simple",
		// 	"title": "ERPNext",
		// 	"version": "12.2.0"
		// }];

		if (
			!Array.isArray(change_log) ||
			!change_log.length ||
			window.Cypress ||
			cint(kanivin.boot.sysdefaults.disable_change_log_notification)
		) {
			return;
		}

		// Iterate over changelog
		var change_log_dialog = kanivin.msgprint({
			message: kanivin.render_template("change_log", { change_log: change_log }),
			title: __("Updated To A New Version 🎉"),
			wide: true,
		});
		change_log_dialog.keep_open = true;
		change_log_dialog.custom_onhide = function () {
			kanivin.call({
				method: "kanivin.utils.change_log.update_last_known_versions",
			});
			me.show_notes();
		};
	}

	show_update_available() {
		if (!kanivin.boot.has_app_updates) return;
		kanivin.xcall("kanivin.utils.change_log.show_update_popup");
	}

	add_browser_class() {
		$("html").addClass(kanivin.utils.get_browser().name.toLowerCase());
	}

	set_fullwidth_if_enabled() {
		kanivin.ui.toolbar.set_fullwidth_if_enabled();
	}

	show_notes() {
		var me = this;
		if (kanivin.boot.notes.length) {
			kanivin.boot.notes.forEach(function (note) {
				if (!note.seen || note.notify_on_every_login) {
					var d = kanivin.msgprint({ message: note.content, title: note.title });
					d.keep_open = true;
					d.custom_onhide = function () {
						note.seen = true;

						// Mark note as read if the Notify On Every Login flag is not set
						if (!note.notify_on_every_login) {
							kanivin.call({
								method: "kanivin.desk.doctype.note.note.mark_as_seen",
								args: {
									note: note.name,
								},
							});
						}

						// next note
						me.show_notes();
					};
				}
			});
		}
	}

	setup_build_events() {
		if (kanivin.boot.developer_mode) {
			kanivin.require("build_events.bundle.js");
		}
	}

	setup_energy_point_listeners() {
		kanivin.realtime.on("energy_point_alert", (message) => {
			kanivin.show_alert(message);
		});
	}

	setup_copy_doc_listener() {
		$("body").on("paste", (e) => {
			try {
				let pasted_data = kanivin.utils.get_clipboard_data(e);
				let doc = JSON.parse(pasted_data);
				if (doc.doctype) {
					e.preventDefault();
					const sleep = kanivin.utils.sleep;

					kanivin.dom.freeze(__("Creating {0}", [doc.doctype]) + "...");
					// to avoid abrupt UX
					// wait for activity feedback
					sleep(500).then(() => {
						let res = kanivin.model.with_doctype(doc.doctype, () => {
							let newdoc = kanivin.model.copy_doc(doc);
							newdoc.__newname = doc.name;
							delete doc.name;
							newdoc.idx = null;
							newdoc.__run_link_triggers = false;
							kanivin.set_route("Form", newdoc.doctype, newdoc.name);
							kanivin.dom.unfreeze();
						});
						res && res.fail?.(kanivin.dom.unfreeze);
					});
				}
			} catch (e) {
				//
			}
		});
	}

	/// Setup event listeners for events across browser tabs / web workers.
	setup_broadcast_listeners() {
		// booted in another tab -> refresh csrf to avoid invalid requests.
		kanivin.broadcast.on("boot", ({ csrf_token, user }) => {
			if (user && user != kanivin.session.user) {
				kanivin.msgprint({
					message: __(
						"You've logged in as another user from another tab. Refresh this page to continue using system."
					),
					title: __("User Changed"),
					primary_action: {
						label: __("Refresh"),
						action: () => {
							window.location.reload();
						},
					},
				});
				return;
			}

			if (csrf_token) {
				// If user re-logged in then their other tabs won't be usable without this update.
				kanivin.csrf_token = csrf_token;
			}
		});
	}

	setup_moment() {
		moment.updateLocale("en", {
			week: {
				dow: kanivin.datetime.get_first_day_of_the_week_index(),
			},
		});
		moment.locale("en");
		moment.user_utc_offset = moment().utcOffset();
		if (kanivin.boot.timezone_info) {
			moment.tz.add(kanivin.boot.timezone_info);
		}
	}
};

kanivin.get_module = function (m, default_module) {
	var module = kanivin.modules[m] || default_module;
	if (!module) {
		return;
	}

	if (module._setup) {
		return module;
	}

	if (!module.label) {
		module.label = m;
	}

	if (!module._label) {
		module._label = __(module.label);
	}

	module._setup = true;

	return module;
};
