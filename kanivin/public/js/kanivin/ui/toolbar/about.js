kanivin.provide("kanivin.ui.misc");
kanivin.ui.misc.about = function () {
	if (!kanivin.ui.misc.about_dialog) {
		var d = new kanivin.ui.Dialog({ title: __("Kanivin Framework") });

		$(d.body).html(
			repl(
				`<div>
					<p>${__("Open Source Applications for the Web")}</p>
					<p><i class='fa fa-globe fa-fw'></i>
						${__("Website")}:
						<a href='https://kanivinframework.com' target='_blank'>https://kanivinframework.com</a></p>
					<p><i class='fa fa-github fa-fw'></i>
						${__("Source")}:
						<a href='https://github.com/kanivin' target='_blank'>https://github.com/kanivin</a></p>
					<p><i class='fa fa-graduation-cap fa-fw'></i>
						Kanivin School: <a href='https://kanivin.school' target='_blank'>https://kanivin.school</a></p>
					<p><i class='fa fa-linkedin fa-fw'></i>
						Linkedin: <a href='https://linkedin.com/company/kanivin-tech' target='_blank'>https://linkedin.com/company/kanivin-tech</a></p>
					<p><i class='fa fa-twitter fa-fw'></i>
						Twitter: <a href='https://twitter.com/kanivintech' target='_blank'>https://twitter.com/kanivintech</a></p>
					<p><i class='fa fa-youtube fa-fw'></i>
						YouTube: <a href='https://www.youtube.com/@kanivintech' target='_blank'>https://www.youtube.com/@kanivintech</a></p>
					<hr>
					<h4>${__("Installed Apps")}</h4>
					<div id='about-app-versions'>${__("Loading versions...")}</div>
					<hr>
					<p class='text-muted'>${__("&copy; Kanivin Pvt. Ltd. and contributors")} </p>
					</div>`,
				kanivin.app
			)
		);

		kanivin.ui.misc.about_dialog = d;

		kanivin.ui.misc.about_dialog.on_page_show = function () {
			if (!kanivin.versions) {
				kanivin.call({
					method: "kanivin.utils.change_log.get_versions",
					callback: function (r) {
						show_versions(r.message);
					},
				});
			} else {
				show_versions(kanivin.versions);
			}
		};

		var show_versions = function (versions) {
			var $wrap = $("#about-app-versions").empty();
			$.each(Object.keys(versions).sort(), function (i, key) {
				var v = versions[key];
				let text;
				if (v.branch) {
					text = $.format("<p><b>{0}:</b> v{1} ({2})<br></p>", [
						v.title,
						v.branch_version || v.version,
						v.branch,
					]);
				} else {
					text = $.format("<p><b>{0}:</b> v{1}<br></p>", [v.title, v.version]);
				}
				$(text).appendTo($wrap);
			});

			kanivin.versions = versions;
		};
	}

	kanivin.ui.misc.about_dialog.show();
};
