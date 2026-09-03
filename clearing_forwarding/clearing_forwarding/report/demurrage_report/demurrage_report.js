frappe.query_reports["Demurrage Report"] = {
	"filters": [
		{"fieldname": "status", "label": "Status", "fieldtype": "Select",
		 "options": "\nWithin Free Time\nNearing Expiry\nOverdue\nCleared"}
	]
};
