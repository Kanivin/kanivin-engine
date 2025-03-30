// Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
// MIT License. See license.txt

kanivin.provide("kanivin.model");

$.extend(kanivin.model, {
	new_names: {},

	get_new_doc: function (doctype, parent_doc, parentfield, with_mandatory_children) {
		kanivin.provide("locals." + doctype);
		var doc = {
			docstatus: 0,
			doctype: doctype,
			name: kanivin.model.get_new_name(doctype),
			__islocal: 1,
			__unsaved: 1,
			owner: kanivin.session.user,
		};
		kanivin.model.set_default_values(doc, parent_doc);

		if (parent_doc) {
			$.extend(doc, {
				parent: parent_doc.name,
				parentfield: parentfield,
				parenttype: parent_doc.doctype,
			});
			if (!parent_doc[parentfield]) parent_doc[parentfield] = [];
			doc.idx = parent_doc[parentfield].length + 1;
			parent_doc[parentfield].push(doc);
		} else {
			kanivin.provide("kanivin.model.docinfo." + doctype + "." + doc.name);
		}

		kanivin.model.add_to_locals(doc);

		if (with_mandatory_children) {
			kanivin.model.create_mandatory_children(doc);
		}

		if (!parent_doc) {
			doc.__run_link_triggers = 1;
		}

		// set the name if called from a link field
		if (kanivin.route_options && kanivin.route_options.name_field) {
			var meta = kanivin.get_meta(doctype);
			// set title field / name as name
			if (meta.autoname && meta.autoname.indexOf("field:") !== -1) {
				doc[meta.autoname.substr(6)] = kanivin.route_options.name_field;
			} else if (meta.autoname && meta.autoname === "prompt") {
				doc.__newname = kanivin.route_options.name_field;
			} else if (meta.title_field) {
				doc[meta.title_field] = kanivin.route_options.name_field;
			}

			delete kanivin.route_options.name_field;
		}

		// set route options
		if (kanivin.route_options && !doc.parent) {
			$.each(kanivin.route_options, function (fieldname, value) {
				var df = kanivin.meta.has_field(doctype, fieldname);
				if (df && !df.no_copy) {
					doc[fieldname] = value;
				}
			});
			kanivin.route_options = null;
		}

		return doc;
	},

	make_new_doc_and_get_name: function (doctype, with_mandatory_children) {
		return kanivin.model.get_new_doc(doctype, null, null, with_mandatory_children).name;
	},

	get_new_name: function (doctype) {
		// random hash is added to idenity mislinked files when doc is not saved and file is uploaded.
		return kanivin.router.slug(`new-${doctype}-${kanivin.utils.get_random(10)}`);
	},

	set_default_values: function (doc, parent_doc) {
		let doctype = doc.doctype;
		let docfields = kanivin.meta.get_docfields(doctype);
		let updated = [];

		// Table types should be initialized
		let fieldtypes_without_default = kanivin.model.no_value_type.filter(
			(fieldtype) => !kanivin.model.table_fields.includes(fieldtype)
		);
		docfields.forEach((f) => {
			if (
				fieldtypes_without_default.includes(f.fieldtype) ||
				doc[f.fieldname] != null ||
				f.no_default
			) {
				return;
			}

			let v = kanivin.model.get_default_value(f, doc, parent_doc);
			if (v) {
				if (["Int", "Check"].includes(f.fieldtype)) v = cint(v);
				else if (["Currency", "Float"].includes(f.fieldtype)) v = flt(v);

				doc[f.fieldname] = v;
				updated.push(f.fieldname);
			} else if (
				f.fieldtype == "Select" &&
				f.options &&
				typeof f.options === "string" &&
				!["[Select]", "Loading..."].includes(f.options)
			) {
				doc[f.fieldname] = f.options.split("\n")[0];
			}
		});
		return updated;
	},

	create_mandatory_children: function (doc) {
		var meta = kanivin.get_meta(doc.doctype);
		if (meta && meta.istable) return;

		// create empty rows for mandatory table fields
		kanivin.meta.get_docfields(doc.doctype).forEach(function (df) {
			if (df.fieldtype === "Table" && df.reqd) {
				kanivin.model.add_child(doc, df.fieldname);
			}
		});
	},

	get_default_value: function (df, doc, parent_doc) {
		var user_default = "";
		var user_permissions = kanivin.defaults.get_user_permissions();
		let allowed_records = [];
		let default_doc = null;
		let value = null;
		if (user_permissions) {
			({ allowed_records, default_doc } = kanivin.perm.filter_allowed_docs_for_doctype(
				user_permissions[df.options],
				doc.doctype
			));
		}
		var meta = kanivin.get_meta(doc.doctype);
		var has_user_permissions =
			df.fieldtype === "Link" &&
			!$.isEmptyObject(user_permissions) &&
			df.ignore_user_permissions != 1 &&
			allowed_records.length;

		// don't set defaults for "User" link field using User Permissions!
		if (df.fieldtype === "Link" && df.options !== "User") {
			// If user permission has Is Default enabled or single-user permission has found against respective doctype.
			if (has_user_permissions && default_doc) {
				value = default_doc;
			} else {
				// 2 - look in user defaults

				if (!df.ignore_user_permissions) {
					var user_defaults = kanivin.defaults.get_user_defaults(df.options);
					if (user_defaults && user_defaults.length === 1) {
						// Use User Permission value when only when it has a single value
						user_default = user_defaults[0];
					}
				}

				if (!user_default) {
					user_default = kanivin.defaults.get_user_default(df.fieldname);
				}
				if (
					!user_default &&
					df.remember_last_selected_value &&
					kanivin.boot.user.last_selected_values
				) {
					user_default = kanivin.boot.user.last_selected_values[df.options];
				}

				var is_allowed_user_default =
					user_default &&
					(!has_user_permissions || allowed_records.includes(user_default));

				// is this user default also allowed as per user permissions?
				if (is_allowed_user_default) {
					value = user_default;
				}
			}
		}

		// 3 - look in default of docfield
		if (!value || df["default"]) {
			const default_val = String(df["default"]);
			if (default_val == "__user" || default_val.toLowerCase() == "user") {
				value = kanivin.session.user;
			} else if (default_val == "user_fullname") {
				value = kanivin.session.user_fullname;
			} else if (default_val == "Today") {
				value = kanivin.datetime.get_today();
			} else if ((default_val || "").toLowerCase() === "now") {
				if (df.fieldtype == "Time") {
					value = kanivin.datetime.now_time();
				} else {
					// datetime fields are stored in system tz
					value = kanivin.datetime.system_datetime();
				}
			} else if (default_val[0] === ":") {
				var boot_doc = kanivin.model.get_default_from_boot_docs(df, doc, parent_doc);
				var is_allowed_boot_doc =
					!has_user_permissions || allowed_records.includes(boot_doc);

				if (is_allowed_boot_doc) {
					value = boot_doc;
				}
			} else if (df.fieldname === meta.title_field) {
				// ignore defaults for title field
				value = "";
			} else {
				// is this default value is also allowed as per user permissions?
				var is_allowed_default =
					!has_user_permissions || allowed_records.includes(df.default);
				if (df.fieldtype !== "Link" || df.options === "User" || is_allowed_default) {
					value = df["default"];
				}
			}
		} else if (df.fieldtype == "Time") {
			value = kanivin.datetime.now_time();
		}

		if (kanivin.model.table_fields.includes(df.fieldtype)) {
			value = [];
		}

		// set it here so we know it was set as a default
		df.__default_value = value;

		return value;
	},

	get_default_from_boot_docs: function (df, doc, parent_doc) {
		// set default from partial docs passed during boot like ":User"
		if (kanivin.get_list(df["default"]).length > 0) {
			var ref_fieldname = df["default"].slice(1).toLowerCase().replace(" ", "_");
			var ref_value = parent_doc
				? parent_doc[ref_fieldname]
				: kanivin.defaults.get_user_default(ref_fieldname);
			var ref_doc = ref_value ? kanivin.get_doc(df["default"], ref_value) : null;

			if (ref_doc && ref_doc[df.fieldname]) {
				return ref_doc[df.fieldname];
			}
		}
	},

	add_child: function (parent_doc, doctype, parentfield, idx) {
		// if given doc, fieldname only
		if (arguments.length === 2) {
			parentfield = doctype;
			doctype = kanivin.meta.get_field(parent_doc.doctype, parentfield).options;
		}

		// create row doc
		idx = idx ? idx - 0.1 : (parent_doc[parentfield] || []).length + 1;

		var child = kanivin.model.get_new_doc(doctype, parent_doc, parentfield);
		child.idx = idx;

		// renum for fraction
		if (idx !== cint(idx)) {
			var sorted = parent_doc[parentfield].sort(function (a, b) {
				return a.idx - b.idx;
			});
			for (var i = 0, j = sorted.length; i < j; i++) {
				var d = sorted[i];
				d.idx = i + 1;
			}
		}

		if (cur_frm && cur_frm.doc == parent_doc) cur_frm.dirty();

		return child;
	},

	copy_doc: function (doc, from_amend, parent_doc, parentfield) {
		let no_copy_list = ["name", "amended_from", "amendment_date", "cancel_reason"];
		let newdoc = kanivin.model.get_new_doc(doc.doctype, parent_doc, parentfield);

		for (let key in doc) {
			// don't copy name and blank fields
			let df = kanivin.meta.get_docfield(doc.doctype, key);

			const is_internal_field = key.substring(0, 2) === "__";
			const is_blocked_field = no_copy_list.includes(key);
			const is_no_copy = !from_amend && df && cint(df.no_copy) == 1;
			const is_password = df && df.fieldtype === "Password";

			if (df && !is_internal_field && !is_blocked_field && !is_no_copy && !is_password) {
				let value = doc[key] || [];
				if (kanivin.model.table_fields.includes(df.fieldtype)) {
					for (let i = 0, j = value.length; i < j; i++) {
						let d = value[i];
						kanivin.model.copy_doc(d, from_amend, newdoc, df.fieldname);
					}
				} else {
					newdoc[key] = doc[key];
				}
			}
		}

		let user = kanivin.session.user;

		newdoc.__islocal = 1;
		newdoc.docstatus = 0;
		newdoc.owner = user;
		newdoc.creation = "";
		newdoc.modified_by = user;
		newdoc.modified = "";
		newdoc.lft = null;
		newdoc.rgt = null;

		if (from_amend && parent_doc) {
			newdoc._amended_from = doc.name;
		}

		return newdoc;
	},

	open_mapped_doc: function (opts) {
		if (opts.frm && opts.frm.doc.__unsaved) {
			kanivin.throw(
				__("You have unsaved changes in this form. Please save before you continue.")
			);
		} else if (!opts.source_name && opts.frm) {
			opts.source_name = opts.frm.doc.name;
		} else if (!opts.frm && !opts.source_name) {
			opts.source_name = null;
		}

		return kanivin.call({
			type: "POST",
			method: "kanivin.model.mapper.make_mapped_doc",
			args: {
				method: opts.method,
				source_name: opts.source_name,
				args: opts.args || null,
				selected_children: opts.frm ? opts.frm.get_selected() : null,
			},
			freeze: true,
			freeze_message: opts.freeze_message || "",
			callback: function (r) {
				if (!r.exc) {
					kanivin.model.sync(r.message);
					if (opts.run_link_triggers) {
						kanivin.get_doc(
							r.message.doctype,
							r.message.name
						).__run_link_triggers = true;
					}
					kanivin.set_route("Form", r.message.doctype, r.message.name);
				}
			},
		});
	},
});

kanivin.create_routes = {};
kanivin.new_doc = function (doctype, opts, init_callback) {
	if (doctype === "File") {
		new kanivin.ui.FileUploader({
			folder: opts ? opts.folder : "Home",
		});
		return;
	}
	return new Promise((resolve) => {
		if (opts && $.isPlainObject(opts)) {
			kanivin.route_options = opts;
		}
		kanivin.model.with_doctype(doctype, function () {
			if (kanivin.create_routes[doctype]) {
				kanivin.set_route(kanivin.create_routes[doctype]).then(() => resolve());
			} else {
				kanivin.ui.form
					.make_quick_entry(doctype, null, init_callback)
					.then(() => resolve());
			}
		});
	});
};
