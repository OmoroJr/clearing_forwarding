import frappe


def execute(filters=None):
	columns = [
		{"label": "Job", "fieldname": "name", "fieldtype": "Link",
		 "options": "Clearing and Forwarding Job", "width": 140},
		{"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 160},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 150},
		{"label": "Estimated Revenue", "fieldname": "estimated_revenue", "fieldtype": "Currency", "width": 140},
		{"label": "Actual Cost So Far", "fieldname": "actual_cost", "fieldtype": "Currency", "width": 140},
	]

	data = frappe.db.sql("""
		select name, customer, status, estimated_revenue, actual_cost
		from `tabClearing and Forwarding Job`
		where payment_status = 'Not Billed' and docstatus = 1
		order by creation desc
	""", as_dict=1)

	return columns, data
