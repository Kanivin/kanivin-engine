kanivin.route_history_queue = [];
const routes_to_skip = ["Form", "social", "setup-wizard", "recorder"];

const save_routes = kanivin.utils.debounce(() => {
	if (kanivin.session.user === "Guest") return;
	const routes = kanivin.route_history_queue;
	if (!routes.length) return;

	kanivin.route_history_queue = [];

	kanivin
		.xcall("kanivin.desk.doctype.route_history.route_history.deferred_insert", {
			routes: routes,
		})
		.catch(() => {
			kanivin.route_history_queue.concat(routes);
		});
}, 10000);

kanivin.router.on("change", () => {
	const route = kanivin.get_route();
	if (is_route_useful(route)) {
		kanivin.route_history_queue.push({
			creation: kanivin.datetime.now_datetime(),
			route: kanivin.get_route_str(),
		});

		save_routes();
	}
});

function is_route_useful(route) {
	if (!route[1]) {
		return false;
	} else if ((route[0] === "List" && !route[2]) || routes_to_skip.includes(route[0])) {
		return false;
	} else {
		return true;
	}
}
