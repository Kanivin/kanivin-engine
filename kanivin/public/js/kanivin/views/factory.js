// Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
// MIT License. See license.txt

kanivin.provide("kanivin.pages");
kanivin.provide("kanivin.views");

kanivin.views.Factory = class Factory {
	constructor(opts) {
		$.extend(this, opts);
	}

	show() {
		this.route = kanivin.get_route();
		this.page_name = kanivin.get_route_str();

		if (this.before_show && this.before_show() === false) return;

		if (kanivin.pages[this.page_name]) {
			kanivin.container.change_to(this.page_name);
			if (this.on_show) {
				this.on_show();
			}
		} else {
			if (this.route[1]) {
				this.make(this.route);
			} else {
				kanivin.show_not_found(this.route);
			}
		}
	}

	make_page(double_column, page_name, hide_sidebar) {
		return kanivin.make_page(double_column, page_name, hide_sidebar);
	}
};

kanivin.make_page = function (double_column, page_name, disable_sidebar_toggle) {
	if (!page_name) {
		page_name = kanivin.get_route_str();
	}

	const page = kanivin.container.add_page(page_name);

	kanivin.ui.make_app_page({
		parent: page,
		single_column: !double_column,
		disable_sidebar_toggle: disable_sidebar_toggle,
	});

	kanivin.container.change_to(page_name);
	return page;
};
