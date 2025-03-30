// Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
// MIT License. See license.txt

// for translation
kanivin._ = function (txt, replace, context = null) {
	if (!txt) return txt;
	if (typeof txt != "string") return txt;

	let translated_text = "";

	let key = txt; // txt.replace(/\n/g, "");
	if (context) {
		translated_text = kanivin._messages[`${key}:${context}`];
	}

	if (!translated_text) {
		translated_text = kanivin._messages[key] || txt;
	}

	if (replace && typeof replace === "object") {
		translated_text = $.format(translated_text, replace);
	}
	return translated_text;
};

window.__ = kanivin._;

kanivin.get_languages = function () {
	if (!kanivin.languages) {
		kanivin.languages = [];
		$.each(kanivin.boot.lang_dict, function (lang, value) {
			kanivin.languages.push({ label: lang, value: value });
		});
		kanivin.languages = kanivin.languages.sort(function (a, b) {
			return a.value < b.value ? -1 : 1;
		});
	}
	return kanivin.languages;
};
