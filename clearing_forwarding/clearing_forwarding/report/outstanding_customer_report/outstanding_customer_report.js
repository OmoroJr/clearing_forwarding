// Copyright (c) 2026, Clearing Forwarding and contributors
// For license information, please see license.txt

frappe.query_reports["Outstanding Customer Report"] = {
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
			fieldname: "payment_status",
			label: __("Payment Status"),
			fieldtype: "Select",
			options: "\nNot Billed\nBilled\nPartially Paid\nPaid",
		},
		{
			fieldname: "min_outstanding",
			label: __("Min. Outstanding Amount"),
			fieldtype: "Currency",
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
		if (column.fieldname == "days_outstanding" && data && data.days_outstanding > 30) {
			value = `<span style="color: #c62828; font-weight: 600;">${value}</span>`;
		}
		return value;
	},
};
