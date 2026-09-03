import frappe


def execute(filters=None):
	filters = filters or {}
	conditions = []
	values = {}
	if filters.get("job"):
		conditions.append("job = %(job)s")
		values["job"] = filters["job"]
	if filters.get("cost_type"):
		conditions.append("cost_type = %(cost_type)s")
		values["cost_type"] = filters["cost_type"]
	if filters.get("from_date"):
		conditions.append("posting_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append("posting_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]
	where = ("where " + " and ".join(conditions)) if conditions else ""

	columns = [
		{"label": "Job", "fieldname": "job", "fieldtype": "Link",
		 "options": "Clearing and Forwarding Job", "width": 140},
		{"label": "Cost Type", "fieldname": "cost_type", "fieldtype": "Data", "width": 140},
		{"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 150},
		{"label": "Purchase Invoice", "fieldname": "purchase_invoice", "fieldtype": "Link",
		 "options": "Purchase Invoice", "width": 140},
		{"label": "Container", "fieldname": "container", "fieldtype": "Link", "options": "Container", "width": 120},
		{"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
		{"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 110},
	]

	data = frappe.db.sql(f"""
		select job, cost_type, supplier, purchase_invoice, container, posting_date, amount
		from `tabJob Cost Entry`
		{where}
		order by posting_date desc
	""", values, as_dict=1)

	return columns, data
