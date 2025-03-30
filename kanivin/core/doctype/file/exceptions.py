import kanivin


class MaxFileSizeReachedError(kanivin.ValidationError):
	pass


class FolderNotEmpty(kanivin.ValidationError):
	pass


class FileTypeNotAllowed(kanivin.ValidationError):
	pass


from kanivin.exceptions import *
