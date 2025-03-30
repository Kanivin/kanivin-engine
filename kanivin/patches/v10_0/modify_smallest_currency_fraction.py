# Copyright (c) 2018, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import kanivin


def execute():
	kanivin.db.set_value("Currency", "USD", "smallest_currency_fraction_value", "0.01")
