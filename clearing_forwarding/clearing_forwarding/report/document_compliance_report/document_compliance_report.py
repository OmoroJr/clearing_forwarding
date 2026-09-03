import frappe


def execute(filters=None):
	filters = filters or {}
	conditions = []
	values = {}
	if filters.get("job_type"):
		conditions.append("j.job_type = %(job_type)s")
		values["job_type"] = filters["job_type"]
	where = ("where " + " and ".join(conditions)) if conditions else ""

	columns = [
		{"label": "Job", "fieldname": "job", "fieldtype": "Link",
		 "options": "Clearing and Forwarding Job", "width": 140},
		{"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
		{"label": "Job Type", "fieldname": "job_type", "fieldtype": "Data", "width": 130},
		{"label": "Required Docs", "fieldname": "required_count", "fieldtype": "Int", "width": 110},
		{"label": "Received", "fieldname": "received_count", "fieldtype": "Int", "width": 90},
		{"label": "Verified", "fieldname": "verified_count", "fieldtype": "Int", "width": 90},
		{"label": "Compliance %", "fieldname": "compliance_percent", "fieldtype": "Percent", "width": 100},
		{"label": "Missing Documents", "fieldname": "missing", "fieldtype": "Data", "width": 220},
	]

	jobs = frappe.db.sql(f"""
		select j.name, j.customer, j.job_type
		from `tabClearing and Forwarding Job` j
		{where}
		order by j.creation desc
	""", values, as_dict=1)

	data = []
	for j in jobs:
		docs = frappe.get_all(
			"CF Job Document",
			filters={"parent": j.name, "parenttype": "Clearing and Forwarding Job"},
			fields=["document_type", "required", "received", "verified"],
		)
		required_docs = [d for d in docs if d.required]
		received_count = len([d for d in required_docs if d.received])
		verified_count = len([d for d in required_docs if d.verified])
		missing = [d.document_type for d in required_docs if not d.received]

		data.append({
			"job": j.name,
			"customer": j.customer,
			"job_type": j.job_type,
			"required_count": len(required_docs),
			"received_count": received_count,
			"verified_count": verified_count,
			"compliance_percent": (received_count / len(required_docs) * 100) if required_docs else 100,
			"missing": ", ".join(missing),
		})

	return columns, data
