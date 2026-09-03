frappe.query_reports["Job Register"] = {
	"filters": [
		{"fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer"},
		{"fieldname": "status", "label": "Status", "fieldtype": "Select",
		 "options": "\nDraft\nQuoted\nJob Open\nDocumentation Pending\nDocuments Complete\n"
		            "Customs Processing\nCustoms Assessment\nDuty Pending\nDuty Paid\nCustoms Released\n"
		            "Port Processing\nCargo Released\nTransport Scheduled\nIn Transit\nDelivered\n"
		            "Billing Pending\nBilled\nPayment Pending\nCompleted\nCancelled"},
		{"fieldname": "branch", "label": "Branch", "fieldtype": "Link", "options": "Branch"},
		{"fieldname": "from_date", "label": "From Date", "fieldtype": "Date"},
		{"fieldname": "to_date", "label": "To Date", "fieldtype": "Date"}
	]
};
