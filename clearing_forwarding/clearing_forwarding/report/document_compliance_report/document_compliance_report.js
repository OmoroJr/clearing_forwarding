// Copyright (c) 2026, Clearing Forwarding and contributors
// For license information, please see license.txt

frappe.query_reports["Document Compliance Report"] = {
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
			fieldname: "branch",
			label: __("Branch"),
			fieldtype: "Link",
			options: "Branch",
		},
		{
			fieldname: "document_type",
			label: __("Document Type"),
			fieldtype: "Data",
		},
		{
			fieldname: "issuing_agency",
			label: __("Issuing Agency"),
			fieldtype: "Link",
			options: "Government Agency",
		},
		{
			fieldname: "only_missing",
			label: __("Only Missing (Required, Not Received)"),
			fieldtype: "Check",
		},
		{
			fieldname: "only_unverified",
			label: __("Only Pending Verification"),
			fieldtype: "Check",
		},
		{
			fieldname: "expiring_within_days",
			label: __("Expiring Within (Days)"),
			fieldtype: "Int",
		},
	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname == "compliance_status" && data) {
			const colors = {
				Missing: "#c62828",
				Expired: "#c62828",
				"Pending Verification": "#ef6c00",
				"Expiring Soon": "#f9a825",
				Verified: "#2e7d32",
			};
			const color = colors[data.compliance_status];
			if (color) {
				value = `<span style="color: ${color}; font-weight: 600;">${value}</span>`;
			}
		}
		return value;
	},
};
