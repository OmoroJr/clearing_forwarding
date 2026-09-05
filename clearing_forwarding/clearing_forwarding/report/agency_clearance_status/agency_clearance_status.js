// Copyright (c) 2026, Clearing Forwarding and contributors
// For license information, please see license.txt

frappe.query_reports["Agency Clearance Status"] = {
	"filters": [
		{
			fieldname: "job",
			label: __("Job"),
			fieldtype: "Link",
			options: "Clearing and Forwarding Job",
		},
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer",
		},
		{
			fieldname: "agency",
			label: __("Agency"),
			fieldtype: "Link",
			options: "Government Agency",
		},
		{
			fieldname: "status",
			label: __("Clearance Status"),
			fieldtype: "Select",
			options: "\nPending\nIn Progress\nCleared\nRejected",
		},
	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname == "status" && data) {
			const colors = { Pending: "#ef6c00", Rejected: "#c62828", Cleared: "#2e7d32" };
			const color = colors[data.status];
			if (color) {
				value = `<span style="color: ${color}; font-weight: 600;">${value}</span>`;
			}
		}
		return value;
	},
};
