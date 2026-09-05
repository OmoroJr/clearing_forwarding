// Copyright (c) 2026, Clearing Forwarding and contributors
// For license information, please see license.txt

frappe.query_reports["Shipment Incident Report"] = {
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
			fieldname: "incident_type",
			label: __("Incident Type"),
			fieldtype: "Select",
			options: "\nCargo Damage\nMissing Cargo\nCustoms Issue\nPort Delay\nVehicle Breakdown\nAccident\nDocumentation Error\nContainer Damage\nCustomer Rejection\nOther",
		},
		{
			fieldname: "severity",
			label: __("Severity"),
			fieldtype: "Select",
			options: "\nLow\nMedium\nHigh\nCritical",
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nOpen\nIn Progress\nResolved\nClosed",
		},
		{
			fieldname: "responsible_person",
			label: __("Responsible Person"),
			fieldtype: "Link",
			options: "User",
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Datetime",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -3),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Datetime",
			default: frappe.datetime.get_today(),
		},
	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname == "severity" && data) {
			const colors = { Critical: "#c62828", High: "#ef6c00" };
			const color = colors[data.severity];
			if (color) {
				value = `<span style="color: ${color}; font-weight: 600;">${value}</span>`;
			}
		}
		return value;
	},
};
