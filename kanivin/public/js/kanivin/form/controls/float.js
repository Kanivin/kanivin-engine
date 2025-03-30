kanivin.ui.form.ControlFloat = class ControlFloat extends kanivin.ui.form.ControlInt {
	parse(value) {
		value = this.eval_expression(value);
		return isNaN(parseFloat(value)) ? null : flt(value, this.get_precision());
	}

	format_for_input(value) {
		var number_format;
		if (this.df.fieldtype === "Float" && this.df.options && this.df.options.trim()) {
			number_format = this.get_number_format();
		}
		var formatted_value = format_number(value, number_format, this.get_precision());
		return isNaN(Number(value)) ? "" : formatted_value;
	}

	get_number_format() {
		var currency = kanivin.meta.get_field_currency(this.df, this.get_doc());
		return get_number_format(currency);
	}

	get_precision() {
		// round based on field precision or float precision, else don't round
		return this.df.precision || cint(kanivin.boot.sysdefaults.float_precision, null);
	}
};

kanivin.ui.form.ControlPercent = kanivin.ui.form.ControlFloat;
