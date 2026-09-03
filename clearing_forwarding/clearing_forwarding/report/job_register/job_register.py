import frappe


def execute(filters=None):
	filters = filters or {}
	conditions = []
	values = {}

	if filters.get("customer"):
		conditions.append("customer = %(customer)s")
		values["customer"] = filters["customer"]
	if filters.get("status"):
		conditions.append("status = %(status)s")
		values["status"] = filters["status"]
	if filters.get("branch"):
		conditions.append("branch = %(branch)s")
		values["branch"] = filters["branch"]
	if filters.get("from_date"):
		conditions.append("creation >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append("creation <= %(to_date)s")
		values["to_date"] = filters["to_date"]

	where = ("where " + " and ".join(conditions)) if conditions else ""

	columns = [
		{"label": "Job", "fieldname": "name", "fieldtype": "Link",
		 "options": "Clearing and Forwarding Job", "width": 140},
		{"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 160},
		{"label": "Job Type", "fieldname": "job_type", "fieldtype": "Data", "width": 130},
		{"label": "Branch", "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 100},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 150},
		{"label": "Estimated Revenue", "fieldname": "estimated_revenue", "fieldtype": "Currency", "width": 130},
		{"label": "Actual Revenue", "fieldname": "actual_revenue", "fieldtype": "Currency", "width": 130},
		{"label": "Gross Profit", "fieldname": "gross_profit", "fieldtype": "Currency", "width": 120},
		{"label": "Payment Status", "fieldname": "payment_status", "fieldtype": "Data", "width": 120},
	]

	data = frappe.db.sql(f"""
		select name, customer, job_type, branch, status,
		       estimated_revenue, actual_revenue, gross_profit, payment_status
		from `tabClearing and Forwarding Job`
		{where}
		order by creation desc
	""", values, as_dict=1)

	return columns, data
