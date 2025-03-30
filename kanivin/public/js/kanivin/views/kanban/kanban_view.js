import KanbanSettings from "./kanban_settings";

kanivin.provide("kanivin.views");

kanivin.views.KanbanView = class KanbanView extends kanivin.views.ListView {
	static no_sidebar = true;

	static load_last_view() {
		const route = kanivin.get_route();
		if (route.length === 3) {
			const doctype = route[1];
			const user_settings = kanivin.get_user_settings(doctype)["Kanban"] || {};
			if (!user_settings.last_kanban_board) {
				return new kanivin.views.KanbanView({ doctype: doctype });
			}

			route.push(user_settings.last_kanban_board);
			kanivin.set_route(route);
			return true;
		}
		return false;
	}

	get view_name() {
		return "Kanban";
	}

	show() {
		kanivin.views.KanbanView.get_kanbans(this.doctype).then((kanbans) => {
			if (!kanbans.length) {
				return kanivin.views.KanbanView.show_kanban_dialog(this.doctype, true);
			} else if (kanbans.length && kanivin.get_route().length !== 4) {
				return kanivin.views.KanbanView.show_kanban_dialog(this.doctype, true);
			} else {
				this.kanbans = kanbans;

				return kanivin.run_serially([
					() => this.show_skeleton(),
					() => this.fetch_meta(),
					() => this.hide_skeleton(),
					() => this.check_permissions(),
					() => this.init(),
					() => this.before_refresh(),
					() => this.refresh(),
				]);
			}
		});
	}

	init() {
		return super.init().then(() => {
			let menu_length = this.page.menu.find(".dropdown-item").length;
			if (menu_length === 1) {
				// Only 'Refresh' (hidden) is present (always), dropdown is visibly empty
				this.page.hide_menu();
			}
		});
	}

	setup_defaults() {
		return super.setup_defaults().then(() => {
			let get_board_name = () => {
				return this.kanbans.length && this.kanbans[0].name;
			};

			this.board_name = kanivin.get_route()[3] || get_board_name() || null;
			this.page_title = __(this.board_name);
			this.card_meta = this.get_card_meta();
			this.page_length = 0;

			return kanivin.run_serially([
				() => this.set_board_perms_and_push_menu_items(),
				() => this.get_board(),
			]);
		});
	}

	set_board_perms_and_push_menu_items() {
		// needs server-side call as client-side document instance is absent before kanban render
		return kanivin.call({
			method: "kanivin.client.get_doc_permissions",
			args: {
				doctype: "Kanban Board",
				docname: this.board_name,
			},
			callback: (result) => {
				this.board_perms = result.message.permissions || {};
				this.push_menu_items();
			},
		});
	}

	push_menu_items() {
		if (this.board_perms.write) {
			this.menu_items.push({
				label: __("Save filters"),
				action: () => {
					this.save_kanban_board_filters();
				},
			});
		}

		if (this.board_perms.delete) {
			this.menu_items.push({
				label: __("Delete Kanban Board"),
				action: () => {
					kanivin.confirm(__("Are you sure you want to proceed?"), () => {
						kanivin.db.delete_doc("Kanban Board", this.board_name).then(() => {
							kanivin.show_alert(`Kanban Board ${this.board_name} deleted.`);
							kanivin.set_route("List", this.doctype, "List");
						});
					});
				},
			});
		}
	}

	setup_paging_area() {
		// pass
	}

	toggle_result_area() {
		this.$result.toggle(this.data.length > 0);
	}

	get_board() {
		return kanivin.db.get_doc("Kanban Board", this.board_name).then((board) => {
			this.board = board;
			this.board.filters_array = JSON.parse(this.board.filters || "[]");
			this.board.fields = JSON.parse(this.board.fields || "[]");
			this.filters = this.board.filters_array;
		});
	}

	setup_page() {
		this.hide_page_form = true;
		this.hide_card_layout = true;
		this.hide_sort_selector = true;
		super.setup_page();
	}

	setup_view() {
		if (this.board.columns.filter((col) => col.status !== "Archived").length > 5) {
			this.page.container.addClass("full-width");
		}
		this.setup_realtime_updates();
		this.setup_like();
	}

	set_fields() {
		super.set_fields();
		this._add_field(this.card_meta.title_field);
	}

	before_render() {
		kanivin.model.user_settings.save(this.doctype, "last_view", this.view_name);
		this.save_view_user_settings({
			last_kanban_board: this.board_name,
		});
	}

	render_list() {}

	on_filter_change() {
		if (!this.board_perms.write) return; // avoid misleading ux

		if (JSON.stringify(this.board.filters_array) !== JSON.stringify(this.filter_area.get())) {
			this.page.set_indicator(__("Not Saved"), "orange");
		} else {
			this.page.clear_indicator();
		}
	}

	save_kanban_board_filters() {
		const filters = this.filter_area.get();

		kanivin.db.set_value("Kanban Board", this.board_name, "filters", filters).then((r) => {
			if (r.exc) {
				kanivin.show_alert({
					indicator: "red",
					message: __("There was an error saving filters"),
				});
				return;
			}
			kanivin.show_alert({
				indicator: "green",
				message: __("Filters saved"),
			});

			this.board.filters_array = filters;
			this.on_filter_change();
		});
	}

	get_fields() {
		this.fields.push([this.board.field_name, this.board.reference_doctype]);
		return super.get_fields();
	}

	render() {
		const board_name = this.board_name;
		if (!this.kanban) {
			this.kanban = new kanivin.views.KanbanBoard({
				doctype: this.doctype,
				board: this.board,
				board_name: board_name,
				cards: this.data,
				card_meta: this.card_meta,
				wrapper: this.$result,
				cur_list: this,
				user_settings: this.view_user_settings,
			});
		} else if (board_name === this.kanban.board_name) {
			this.kanban.update(this.data);
		}
	}

	get_card_meta() {
		var meta = kanivin.get_meta(this.doctype);
		// preserve route options erased by new doc
		let route_options = { ...kanivin.route_options };
		var doc = kanivin.model.get_new_doc(this.doctype);
		kanivin.route_options = route_options;
		var title_field = null;
		var quick_entry = false;

		if (this.meta.title_field) {
			title_field = kanivin.meta.get_field(this.doctype, this.meta.title_field);
		}

		this.meta.fields.forEach((df) => {
			const is_valid_field =
				["Data", "Text", "Small Text", "Text Editor"].includes(df.fieldtype) && !df.hidden;

			if (is_valid_field && !title_field) {
				// can be mapped to textarea
				title_field = df;
			}
		});

		// quick entry
		var mandatory = meta.fields.filter((df) => df.reqd && !doc[df.fieldname]);

		if (
			mandatory.some((df) => kanivin.model.table_fields.includes(df.fieldtype)) ||
			mandatory.length > 1
		) {
			quick_entry = true;
		}

		if (!title_field) {
			title_field = kanivin.meta.get_field(this.doctype, "name");
		}

		return {
			quick_entry: quick_entry,
			title_field: title_field,
		};
	}

	get_view_settings() {
		return {
			label: __("Kanban Settings", null, "Button in kanban view menu"),
			action: () => this.show_kanban_settings(),
			standard: true,
		};
	}

	show_kanban_settings() {
		kanivin.model.with_doctype(this.doctype, () => {
			new KanbanSettings({
				kanbanview: this,
				doctype: this.doctype,
				settings: this.board,
				meta: kanivin.get_meta(this.doctype),
			});
		});
	}

	get required_libs() {
		return "kanban_board.bundle.js";
	}
};

kanivin.views.KanbanView.get_kanbans = function (doctype) {
	let kanbans = [];

	return get_kanban_boards().then((kanban_boards) => {
		if (kanban_boards) {
			kanban_boards.forEach((board) => {
				let route = `/app/${kanivin.router.slug(board.reference_doctype)}/view/kanban/${
					board.name
				}`;
				kanbans.push({ name: board.name, route: route });
			});
		}

		return kanbans;
	});

	function get_kanban_boards() {
		return kanivin
			.call("kanivin.desk.doctype.kanban_board.kanban_board.get_kanban_boards", { doctype })
			.then((r) => r.message);
	}
};

kanivin.views.KanbanView.show_kanban_dialog = function (doctype) {
	let dialog = new_kanban_dialog();
	dialog.show();

	function make_kanban_board(board_name, field_name, project) {
		return kanivin.call({
			method: "kanivin.desk.doctype.kanban_board.kanban_board.quick_kanban_board",
			args: {
				doctype,
				board_name,
				field_name,
				project,
			},
			callback: function (r) {
				var kb = r.message;
				if (kb.filters) {
					kanivin.provide("kanivin.kanban_filters");
					kanivin.kanban_filters[kb.kanban_board_name] = kb.filters;
				}
				kanivin.set_route("List", doctype, "Kanban", kb.kanban_board_name);
			},
		});
	}

	function new_kanban_dialog() {
		/* Kanban dialog can show either "Save" or "Customize Form" option depending if any Select fields exist in the DocType for Kanban creation
		 */

		const select_fields = kanivin.get_meta(doctype).fields.filter((df) => {
			return df.fieldtype === "Select" && df.fieldname !== "kanban_column";
		});
		const dialog_fields = get_fields_for_dialog(select_fields);
		const to_save = select_fields.length > 0;
		const primary_action_label = to_save ? __("Save") : __("Customize Form");
		const dialog_title = to_save ? __("New Kanban Board") : __("No Select Field Found");

		let primary_action = () => {
			if (to_save) {
				const values = dialog.get_values();
				make_kanban_board(values.board_name, values.field_name, values.project).then(
					() => dialog.hide(),
					(err) => kanivin.msgprint(err)
				);
			} else {
				kanivin.set_route("Form", "Customize Form", { doc_type: doctype });
			}
		};

		return new kanivin.ui.Dialog({
			title: dialog_title,
			fields: dialog_fields,
			primary_action_label,
			primary_action,
		});
	}

	function get_fields_for_dialog(select_fields) {
		if (!select_fields.length) {
			return [
				{
					fieldtype: "HTML",
					options: `
					<div>
						<p class="text-medium">
						${__(
							'No fields found that can be used as a Kanban Column. Use the Customize Form to add a Custom Field of type "Select".'
						)}
						</p>
					</div>
				`,
				},
			];
		}

		let fields = [
			{
				fieldtype: "Data",
				fieldname: "board_name",
				label: __("Kanban Board Name"),
				reqd: 1,
				description: ["Note", "ToDo"].includes(doctype)
					? __("This Kanban Board will be private")
					: "",
			},
			{
				fieldtype: "Select",
				fieldname: "field_name",
				label: __("Columns based on"),
				options: select_fields.map((df) => ({ label: df.label, value: df.fieldname })),
				default: select_fields[0],
				reqd: 1,
			},
		];

		if (doctype === "Task") {
			fields.push({
				fieldtype: "Link",
				fieldname: "project",
				label: __("Project"),
				options: "Project",
			});
		}

		return fields;
	}
};
