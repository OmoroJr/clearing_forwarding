// Copyright (c) 2026, Clearing Forwarding and contributors
// For license information, please see license.txt

frappe.query_reports["Container Movement Report"] = {
	"filters": [
		{
			fieldname: "container",
			label: __("Container"),
			fieldtype: "Link",
			options: "Container",
		},
		{
			fieldname: "job",
			label: __("Job"),
			fieldtype: "Link",
			options: "Clearing and Forwarding Job",
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nBooked\nEmpty\nStuffing\nLoaded\nAt Port\nDischarged\nCustoms Hold\nReleased\nGate Out\nIn Transit\nDelivered\nEmpty Returned",
		},
		{
			fieldname: "vehicle",
			label: __("Vehicle"),
			fieldtype: "Link",
			options: "Vehicle",
		},
		{
			fieldname: "driver",
			label: __("Driver"),
			fieldtype: "Link",
			options: "Driver",
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Datetime",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Datetime",
			default: frappe.datetime.get_today(),
		},
	],
};
