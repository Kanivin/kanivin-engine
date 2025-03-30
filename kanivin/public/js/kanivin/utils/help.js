// Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
// MIT License. See license.txt

kanivin.provide("kanivin.help");

kanivin.help.youtube_id = {};

kanivin.help.has_help = function (doctype) {
	return kanivin.help.youtube_id[doctype];
};

kanivin.help.show = function (doctype) {
	if (kanivin.help.youtube_id[doctype]) {
		kanivin.help.show_video(kanivin.help.youtube_id[doctype]);
	}
};

kanivin.help.show_video = function (youtube_id, title) {
	if (kanivin.utils.is_url(youtube_id)) {
		const expression =
			'(?:youtube.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu.be/)([^"&?\\s]{11})';
		youtube_id = youtube_id.match(expression)[1];
	}

	// (kanivin.help_feedback_link || "")
	let dialog = new kanivin.ui.Dialog({
		title: title || __("Help"),
		size: "large",
	});

	let video = $(
		`<div class="video-player" data-plyr-provider="youtube" data-plyr-embed-id="${youtube_id}"></div>`
	);
	video.appendTo(dialog.body);

	dialog.show();
	dialog.$wrapper.addClass("video-modal");

	let plyr;
	kanivin.utils.load_video_player().then(() => {
		plyr = new kanivin.Plyr(video[0], {
			hideControls: true,
			resetOnEnd: true,
		});
	});

	dialog.onhide = () => {
		plyr?.destroy();
	};
};

$("body").on("click", "a.help-link", function () {
	var doctype = $(this).attr("data-doctype");
	doctype && kanivin.help.show(doctype);
});
