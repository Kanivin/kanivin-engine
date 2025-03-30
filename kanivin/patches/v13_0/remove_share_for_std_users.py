import kanivin
import kanivin.share


def execute():
	for user in kanivin.STANDARD_USERS:
		kanivin.share.remove("User", user, user)
