# Copyright (c) 2017, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import kanivin


@kanivin.whitelist()
def get_leaderboard_config():
	leaderboard_config = kanivin._dict()
	leaderboard_hooks = kanivin.get_hooks("leaderboards")
	for hook in leaderboard_hooks:
		leaderboard_config.update(kanivin.get_attr(hook)())

	return leaderboard_config
