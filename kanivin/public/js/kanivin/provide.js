// Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
// MIT License. See license.txt

// provide a namespace
if (!window.kanivin) window.kanivin = {};

kanivin.provide = function (namespace) {
	// docs: create a namespace //
	var nsl = namespace.split(".");
	var parent = window;
	for (var i = 0; i < nsl.length; i++) {
		var n = nsl[i];
		if (!parent[n]) {
			parent[n] = {};
		}
		parent = parent[n];
	}
	return parent;
};

kanivin.provide("locals");
kanivin.provide("kanivin.flags");
kanivin.provide("kanivin.settings");
kanivin.provide("kanivin.utils");
kanivin.provide("kanivin.ui.form");
kanivin.provide("kanivin.modules");
kanivin.provide("kanivin.templates");
kanivin.provide("kanivin.test_data");
kanivin.provide("kanivin.utils");
kanivin.provide("kanivin.model");
kanivin.provide("kanivin.user");
kanivin.provide("kanivin.session");
kanivin.provide("kanivin._messages");
kanivin.provide("locals.DocType");

// for listviews
kanivin.provide("kanivin.listview_settings");
kanivin.provide("kanivin.tour");
kanivin.provide("kanivin.listview_parent_route");

// constants
window.NEWLINE = "\n";
window.TAB = 9;
window.UP_ARROW = 38;
window.DOWN_ARROW = 40;

// proxy for user globals defined in desk.js

// API globals
window.cur_frm = null;
