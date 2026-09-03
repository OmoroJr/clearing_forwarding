import frappe


def execute(filters=None):
	filters = filters or {}
	conditions = []
	values = {}
	if filters.get("customer"):
		conditions.append("customer = %(customer)s")
		values["customer"] = filters["customer"]
	where = ("where " + " and ".join(conditions)) if conditions else ""

	columns = [
		{"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 180},
		{"label": "Job Count", "fieldname": "job_count", "fieldtype": "Int", "width": 90},
		{"label": "Total Estimated Revenue", "fieldname": "estimated_revenue", "fieldtype": "Currency", "width": 150},
		{"label": "Total Actual Revenue", "fieldname": "actual_revenue", "fieldtype": "Currency", "width": 150},
		{"label": "Total Actual Cost", "fieldname": "actual_cost", "fieldtype": "Currency", "width": 140},
		{"label": "Total Gross Profit", "fieldname": "gross_profit", "fieldtype": "Currency", "width": 140},
		{"label": "Avg Margin %", "fieldname": "avg_margin", "fieldtype": "Percent", "width": 100},
	]

	data = frappe.db.sql(f"""
		select customer,
		       count(name) as job_count,
		       sum(estimated_revenue) as estimated_revenue,
		       sum(actual_revenue) as actual_revenue,
		       sum(actual_cost) as actual_cost,
		       sum(gross_profit) as gross_profit,
		       avg(actual_margin_percent) as avg_margin
		from `tabClearing and Forwarding Job`
		{where}
		group by customer
		order by gross_profit desc
	""", values, as_dict=1)

	return columns, data
