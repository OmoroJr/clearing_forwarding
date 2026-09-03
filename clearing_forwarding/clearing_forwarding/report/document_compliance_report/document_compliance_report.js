frappe.query_reports["Document Compliance Report"] = {
	"filters": [
		{"fieldname": "job_type", "label": "Job Type", "fieldtype": "Select",
		 "options": "\nImport Clearing\nExport Clearing\nFreight Forwarding\nAir Cargo\n"
		            "Sea Cargo\nRoad Cargo\nTransit Cargo"}
	]
};
