// Copyright (c) 2026, Clearing Forwarding and contributors
// For license information, please see license.txt

frappe.query_reports["Job Costing Report"] = {
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
			fieldname: "cost_type",
			label: __("Cost Type"),
			fieldtype: "Select",
			options: "\nCustoms Duty\nPort Charges\nShipping Line Charges\nFreight\nTransport\nFuel\nHandling\nStorage\nDemurrage\nDetention\nDocumentation\nClearing Agent\nInspection\nWarehousing\nMiscellaneous",
		},
		{
			fieldname: "supplier",
			label: __("Supplier"),
			fieldtype: "Link",
			options: "Supplier",
		},
		{
			fieldname: "container",
			label: __("Container"),
			fieldtype: "Link",
			options: "Container",
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -3),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
	],
};
