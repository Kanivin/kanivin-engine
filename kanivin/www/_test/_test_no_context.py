import kanivin


# no context object is accepted
def get_context():
	context = kanivin._dict()
	context.body = "Custom Content"
	return context
