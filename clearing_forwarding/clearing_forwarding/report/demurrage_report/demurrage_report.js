// Copyright (c) 2026, Clearing Forwarding and contributors
// For license information, please see license.txt

frappe.query_reports["Demurrage Report"] = {
	"filters": [
		{
			fieldname: "job",
			label: __("Job"),
			fieldtype: "Link",
			options: "Clearing and Forwarding Job",
		},
		{
			fieldname: "container",
			label: __("Container"),
			fieldtype: "Link",
			options: "Container",
		},
		{
			fieldname: "shipping_line",
			label: __("Shipping Line"),
			fieldtype: "Link",
			options: "Shipping Line",
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nWithin Free Time\nNearing Expiry\nOverdue\nCleared",
		},
		{
			fieldname: "only_overdue",
			label: __("Only Overdue"),
			fieldtype: "Check",
		},
		{
			fieldname: "from_date",
			label: __("Free Time Start From"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -3),
		},
		{
			fieldname: "to_date",
			label: __("Free Time Start To"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname == "status" && data && data.status == "Overdue") {
			value = `<span style="color: #c62828; font-weight: 600;">${value}</span>`;
		}
		if (column.fieldname == "days_overdue" && data && data.days_overdue > 0) {
			value = `<span style="color: #c62828; font-weight: 600;">${value}</span>`;
		}
		return value;
	},
};
