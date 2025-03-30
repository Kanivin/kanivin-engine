kanivin.provide("kanivin.model");
kanivin.provide("kanivin.utils");

/**
 * Opens the Website Meta Tag form if it exists for {route}
 * or creates a new doc and opens the form
 */
kanivin.utils.set_meta_tag = function (route) {
	kanivin.db.exists("Website Route Meta", route).then((exists) => {
		if (exists) {
			kanivin.set_route("Form", "Website Route Meta", route);
		} else {
			// new doc
			const doc = kanivin.model.get_new_doc("Website Route Meta");
			doc.__newname = route;
			kanivin.set_route("Form", doc.doctype, doc.name);
		}
	});
};
