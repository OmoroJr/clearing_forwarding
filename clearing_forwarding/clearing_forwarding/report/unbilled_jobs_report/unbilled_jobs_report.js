// Copyright (c) 2026, Clearing Forwarding and contributors
// For license information, please see license.txt

frappe.query_reports["Unbilled Jobs Report"] = {
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
			fieldname: "only_delivered_or_later",
			label: __("Only Delivered or Later"),
			fieldtype: "Check",
			default: 1,
		},
		{
			fieldname: "min_days_since_delivery",
			label: __("Min. Days Since Delivery"),
			fieldtype: "Int",
		},
		{
			fieldname: "from_date",
			label: __("Delivery Date From"),
			fieldtype: "Date",
		},
		{
			fieldname: "to_date",
			label: __("Delivery Date To"),
			fieldtype: "Date",
		},
	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname == "days_since_delivery" && data && data.days_since_delivery > 14) {
			value = `<span style="color: #c62828; font-weight: 600;">${value}</span>`;
		}
		return value;
	},
};
