import frappe

COST_TYPES = [
	"Customs Duty", "Port Charges", "Shipping Line Charges", "Freight", "Transport",
	"Handling", "Storage", "Demurrage", "Detention", "Documentation",
]


def execute(filters=None):
	filters = filters or {}
	conditions = []
	values = {}

	if filters.get("customer"):
		conditions.append("j.customer = %(customer)s")
		values["customer"] = filters["customer"]
	if filters.get("job"):
		conditions.append("j.name = %(job)s")
		values["job"] = filters["job"]
	if filters.get("from_date"):
		conditions.append("j.creation >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append("j.creation <= %(to_date)s")
		values["to_date"] = filters["to_date"]

	where = ("where " + " and ".join(conditions)) if conditions else ""

	jobs = frappe.db.sql(f"""
		select j.name, j.customer, j.job_type, j.bill_of_lading_number, j.container_number,
		       j.actual_revenue, j.actual_cost, j.gross_profit, j.actual_margin_percent
		from `tabClearing and Forwarding Job` j
		{where}
		order by j.creation desc
	""", values, as_dict=1)

	if not jobs:
		return _columns(), []

	job_names = [j.name for j in jobs]
	cost_rows = frappe.db.sql("""
		select job, cost_type, sum(amount) as total
		from `tabJob Cost Entry`
		where job in %(jobs)s
		group by job, cost_type
	""", {"jobs": job_names}, as_dict=1)

	cost_by_job = {}
	for row in cost_rows:
		cost_by_job.setdefault(row.job, {})[row.cost_type] = row.total

	data = []
	for j in jobs:
		costs = cost_by_job.get(j.name, {})
		row = {
			"job": j.name,
			"customer": j.customer,
			"job_type": j.job_type,
			"bl_number": j.bill_of_lading_number,
			"container": j.container_number,
			"revenue": j.actual_revenue or 0,
		}
		other_cost = 0
		for ct in COST_TYPES:
			key = ct.lower().replace(" ", "_")
			row[key] = costs.get(ct, 0)
		for ct, amt in costs.items():
			if ct not in COST_TYPES:
				other_cost += amt
		row["other_cost"] = other_cost
		row["total_cost"] = j.actual_cost or 0
		row["gross_profit"] = j.gross_profit or 0
		row["margin_percent"] = j.actual_margin_percent or 0
		data.append(row)

	return _columns(), data


def _columns():
	columns = [
		{"label": "Job", "fieldname": "job", "fieldtype": "Link",
		 "options": "Clearing and Forwarding Job", "width": 140},
		{"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
		{"label": "Job Type", "fieldname": "job_type", "fieldtype": "Data", "width": 120},
		{"label": "BL Number", "fieldname": "bl_number", "fieldtype": "Data", "width": 110},
		{"label": "Container", "fieldname": "container", "fieldtype": "Data", "width": 110},
		{"label": "Revenue", "fieldname": "revenue", "fieldtype": "Currency", "width": 110},
	]
	for ct in COST_TYPES:
		columns.append({
			"label": ct, "fieldname": ct.lower().replace(" ", "_"),
			"fieldtype": "Currency", "width": 100,
		})
	columns += [
		{"label": "Other Cost", "fieldname": "other_cost", "fieldtype": "Currency", "width": 100},
		{"label": "Total Cost", "fieldname": "total_cost", "fieldtype": "Currency", "width": 110},
		{"label": "Gross Profit", "fieldname": "gross_profit", "fieldtype": "Currency", "width": 110},
		{"label": "Margin %", "fieldname": "margin_percent", "fieldtype": "Percent", "width": 90},
	]
	return columns
