// Copyright (c) 2026, Clearing Forwarding and contributors
// For license information, please see license.txt

frappe.query_reports["Job Register"] = {
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
			fieldname: "import_export",
			label: __("Import / Export"),
			fieldtype: "Select",
			options: "\nImport\nExport",
		},
		{
			fieldname: "mode_of_transport",
			label: __("Mode of Transport"),
			fieldtype: "Select",
			options: "\nSea\nAir\nRoad\nRail",
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nDraft\nQuoted\nJob Open\nDocumentation Pending\nDocuments Complete\nCustoms Processing\nCustoms Assessment\nDuty Pending\nDuty Paid\nCustoms Released\nPort Processing\nCargo Released\nTransport Scheduled\nIn Transit\nDelivered\nBilling Pending\nBilled\nPayment Pending\nCompleted\nCancelled",
		},
		{
			fieldname: "payment_status",
			label: __("Payment Status"),
			fieldtype: "Select",
			options: "\nNot Billed\nBilled\nPartially Paid\nPaid",
		},
		{
			fieldname: "shipping_line",
			label: __("Shipping Line"),
			fieldtype: "Link",
			options: "Shipping Line",
		},
		{
			fieldname: "clearing_agent",
			label: __("Clearing Agent"),
			fieldtype: "Link",
			options: "Clearing Agent",
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
