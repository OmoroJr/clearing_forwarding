frappe.query_reports["Job Costing Report"] = {
	"filters": [
		{"fieldname": "job", "label": "Job", "fieldtype": "Link", "options": "Clearing and Forwarding Job"},
		{"fieldname": "cost_type", "label": "Cost Type", "fieldtype": "Select",
		 "options": "\nCustoms Duty\nPort Charges\nShipping Line Charges\nFreight\nTransport\nFuel\n"
		            "Handling\nStorage\nDemurrage\nDetention\nDocumentation\nClearing Agent\n"
		            "Inspection\nWarehousing\nMiscellaneous"},
		{"fieldname": "from_date", "label": "From Date", "fieldtype": "Date"},
		{"fieldname": "to_date", "label": "To Date", "fieldtype": "Date"}
	]
};
