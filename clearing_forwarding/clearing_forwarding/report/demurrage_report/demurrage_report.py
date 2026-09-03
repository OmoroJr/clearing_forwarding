import frappe


def execute(filters=None):
	filters = filters or {}
	conditions = []
	values = {}
	if filters.get("status"):
		conditions.append("status = %(status)s")
		values["status"] = filters["status"]
	where = ("where " + " and ".join(conditions)) if conditions else ""

	columns = [
		{"label": "Container", "fieldname": "container", "fieldtype": "Link", "options": "Container", "width": 130},
		{"label": "Job", "fieldname": "job", "fieldtype": "Link",
		 "options": "Clearing and Forwarding Job", "width": 140},
		{"label": "Shipping Line", "fieldname": "shipping_line", "fieldtype": "Link",
		 "options": "Shipping Line", "width": 140},
		{"label": "Free Time End", "fieldname": "free_time_end", "fieldtype": "Date", "width": 110},
		{"label": "Days Overdue", "fieldname": "days_overdue", "fieldtype": "Int", "width": 100},
		{"label": "Daily Rate", "fieldname": "daily_rate", "fieldtype": "Currency", "width": 100},
		{"label": "Total Charge", "fieldname": "total_charge", "fieldtype": "Currency", "width": 110},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
	]

	data = frappe.db.sql(f"""
		select container, job, shipping_line, free_time_end, days_overdue,
		       daily_rate, total_charge, status
		from `tabDemurrage And Detention`
		{where}
		order by days_overdue desc
	""", values, as_dict=1)

	return columns, data
