kanivin.ready(() => {
	$(".btn-delete-app").on("click", function(event) {
		kanivin.call({
			method:"kanivin.www.third_party_apps.delete_client",
			args: {"client_id": $(this).data("client_id"),
			}
		}).done(r => location.href="/third_party_apps");
	});
});
