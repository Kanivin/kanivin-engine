import "../lib/posthog.js";

class TelemetryManager {
	constructor() {
		this.enabled = false;

		this.project_id = kanivin.boot.posthog_project_id;
		this.telemetry_host = kanivin.boot.posthog_host;
		this.site_age = kanivin.boot.telemetry_site_age;
		if (cint(kanivin.boot.enable_telemetry) && this.project_id && this.telemetry_host) {
			this.enabled = true;
		}
	}

	initialize() {
		if (!this.enabled) return;
		let disable_decide = !this.should_record_session();
		try {
			posthog.init(this.project_id, {
				api_host: this.telemetry_host,
				autocapture: false,
				capture_pageview: false,
				capture_pageleave: false,
				advanced_disable_decide: disable_decide,
			});
			posthog.identify(kanivin.boot.sitename);
			this.send_heartbeat();
			this.register_pageview_handler();
		} catch (e) {
			console.trace("Failed to initialize telemetry", e);
			this.enabled = false;
		}
	}

	capture(event, app, props) {
		if (!this.enabled) return;
		posthog.capture(`${app}_${event}`, props);
	}

	disable() {
		this.enabled = false;
	}

	can_enable() {
		if (cint(navigator.doNotTrack)) {
			return false;
		}
		let posthog_available = Boolean(this.telemetry_host && this.project_id);
		let sentry_available = Boolean(kanivin.boot.sentry_dsn);
		return posthog_available || sentry_available;
	}

	send_heartbeat() {
		const KEY = "ph_last_heartbeat";
		const now = kanivin.datetime.system_datetime(true);
		const last = localStorage.getItem(KEY);

		if (!last || moment(now).diff(moment(last), "hours") > 12) {
			localStorage.setItem(KEY, now.toISOString());
			this.capture("heartbeat", "kanivin", { kanivin_version: kanivin.boot?.versions?.kanivin });
		}
	}

	register_pageview_handler() {
		if (this.site_age && this.site_age > 6) {
			return;
		}

		kanivin.router.on("change", () => {
			posthog.capture("$pageview");
		});
	}

	should_record_session() {
		let start = kanivin.boot.sysdefaults.session_recording_start;
		if (!start) return;

		let start_datetime = kanivin.datetime.str_to_obj(start);
		let now = kanivin.datetime.now_datetime();
		// if user allowed recording only record for first 2 hours, never again.
		return kanivin.datetime.get_minute_diff(now, start_datetime) < 120;
	}
}

kanivin.telemetry = new TelemetryManager();
kanivin.telemetry.initialize();
