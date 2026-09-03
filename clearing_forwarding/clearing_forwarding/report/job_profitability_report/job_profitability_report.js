frappe.query_reports["Job Profitability Report"] = {
	"filters": [
		{"fieldname": "job", "label": "Job", "fieldtype": "Link", "options": "Clearing and Forwarding Job"},
		{"fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer"},
		{"fieldname": "from_date", "label": "From Date", "fieldtype": "Date"},
		{"fieldname": "to_date", "label": "To Date", "fieldtype": "Date"}
	]
};
