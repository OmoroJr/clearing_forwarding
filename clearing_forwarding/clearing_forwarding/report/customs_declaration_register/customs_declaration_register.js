// Copyright (c) 2026, Clearing Forwarding and contributors
// For license information, please see license.txt

frappe.query_reports["Customs Declaration Register"] = {
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
			fieldname: "import_export",
			label: __("Import / Export"),
			fieldtype: "Select",
			options: "\nImport\nExport",
		},
		{
			fieldname: "customs_station",
			label: __("Customs Station"),
			fieldtype: "Link",
			options: "Government Agency",
		},
		{
			fieldname: "assessment_status",
			label: __("Assessment Status"),
			fieldtype: "Select",
			options: "\nPending\nAssessed",
		},
		{
			fieldname: "clearance_status",
			label: __("Clearance Status"),
			fieldtype: "Select",
			options: "\nPending\nReleased",
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nDraft\nSubmitted\nAssessed\nPayment Pending\nPaid\nCustoms Released\nClosed",
		},
		{
			fieldname: "from_date",
			label: __("Declaration Date From"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -3),
		},
		{
			fieldname: "to_date",
			label: __("Declaration Date To"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
	],
};
