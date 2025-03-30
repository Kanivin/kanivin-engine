import * as Sentry from "@sentry/browser";

Sentry.init({
	dsn: kanivin.boot.sentry_dsn,
	release: kanivin?.boot?.versions?.kanivin,
	autoSessionTracking: false,
	initialScope: {
		// don't use kanivin.session.user, it's set much later and will fail because of async loading
		user: { id: kanivin.boot.sitename },
		tags: { kanivin_user: kanivin.boot.user.name ?? "Unidentified" },
	},
	beforeSend(event, hint) {
		// Check if it was caused by kanivin.throw()
		if (
			hint.originalException instanceof Error &&
			hint.originalException.stack &&
			hint.originalException.stack.includes("kanivin.throw")
		) {
			return null;
		}
		return event;
	},
});
