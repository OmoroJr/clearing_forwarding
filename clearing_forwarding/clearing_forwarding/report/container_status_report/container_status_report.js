// Copyright (c) 2026, Clearing Forwarding and contributors
// For license information, please see license.txt

frappe.query_reports["Container Status Report"] = {
	"filters": [
		{
			fieldname: "job",
			label: __("Job"),
			fieldtype: "Link",
			options: "Clearing and Forwarding Job",
		},
		{
			fieldname: "shipping_line",
			label: __("Shipping Line"),
			fieldtype: "Link",
			options: "Shipping Line",
		},
		{
			fieldname: "container_type",
			label: __("Container Type"),
			fieldtype: "Select",
			options: "\n20ft Standard\n40ft Standard\n40ft High Cube\n20ft Reefer\n40ft Reefer\nOpen Top\nFlat Rack\nOther",
		},
		{
			fieldname: "owner_type",
			label: __("Owner Type"),
			fieldtype: "Select",
			options: "\nShipping Line Owned\nLeased\nCompany Owned",
		},
		{
			fieldname: "container_status",
			label: __("Container Status"),
			fieldtype: "Select",
			options: "\nBooked\nEmpty\nStuffing\nLoaded\nAt Port\nDischarged\nCustoms Hold\nReleased\nGate Out\nIn Transit\nDelivered\nEmpty Returned",
		},
		{
			fieldname: "demurrage_status",
			label: __("Demurrage Status"),
			fieldtype: "Select",
			options: "\nWithin Free Time\nNearing Expiry\nOverdue\nCleared",
		},
		{
			fieldname: "only_active",
			label: __("Only Active (Exclude Empty Returned)"),
			fieldtype: "Check",
			default: 1,
		},
	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname == "demurrage_status" && data && data.demurrage_status == "Overdue") {
			value = `<span style="color: #c62828; font-weight: 600;">${value}</span>`;
		}
		return value;
	},
};
