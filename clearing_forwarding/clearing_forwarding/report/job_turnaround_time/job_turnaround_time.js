// Copyright (c) 2026, Clearing Forwarding and contributors
// For license information, please see license.txt

frappe.query_reports["Job Turnaround Time"] = {
	"filters": [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "branch",
			label: __("Branch"),
			fieldtype: "Link",
			options: "Branch",
		},
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer",
		},
		{
			fieldname: "job_type",
			label: __("Job Type"),
			fieldtype: "Select",
			options: "\nImport Clearing\nExport Clearing\nFreight Forwarding\nAir Cargo\nSea Cargo\nRoad Cargo\nTransit Cargo",
		},
		{
			fieldname: "only_completed",
			label: __("Only Jobs with a Delivery Date"),
			fieldtype: "Check",
			default: 1,
		},
		{
			fieldname: "from_date",
			label: __("Created From"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -6),
		},
		{
			fieldname: "to_date",
			label: __("Created To"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname == "eta_variance_days" && data && data.eta_variance_days > 0) {
			value = `<span style="color: #c62828; font-weight: 600;">${value}</span>`;
		}
		return value;
	},
};
