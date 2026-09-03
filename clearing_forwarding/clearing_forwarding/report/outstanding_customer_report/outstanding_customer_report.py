import frappe


def execute(filters=None):
	columns = [
		{"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 180},
		{"label": "Job Count", "fieldname": "job_count", "fieldtype": "Int", "width": 90},
		{"label": "Billed Amount", "fieldname": "billed_amount", "fieldtype": "Currency", "width": 130},
		{"label": "Outstanding Amount", "fieldname": "outstanding_amount", "fieldtype": "Currency", "width": 140},
	]

	data = frappe.db.sql("""
		select customer,
		       count(name) as job_count,
		       sum(billed_amount) as billed_amount,
		       sum(outstanding_amount) as outstanding_amount
		from `tabClearing and Forwarding Job`
		where outstanding_amount > 0
		group by customer
		order by outstanding_amount desc
	""", as_dict=1)

	return columns, data
