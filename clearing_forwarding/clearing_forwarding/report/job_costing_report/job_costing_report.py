# Copyright (c) 2026, Clearing Forwarding and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	summary = get_summary(data)
	return columns, data, None, chart, summary


def get_columns():
	return [
		{"label": _("Entry"), "fieldname": "name", "fieldtype": "Link", "options": "Job Cost Entry", "width": 150},
		{"label": _("Job"), "fieldname": "job", "fieldtype": "Link", "options": "Clearing and Forwarding Job", "width": 140},
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 120},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 100},
		{"label": _("Cost Type"), "fieldname": "cost_type", "fieldtype": "Data", "width": 130},
		{"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 130},
		{"label": _("Purchase Invoice"), "fieldname": "purchase_invoice", "fieldtype": "Link", "options": "Purchase Invoice", "width": 140},
		{"label": _("Allocation"), "fieldname": "job_cost_allocation", "fieldtype": "Link", "options": "Job Cost Allocation", "width": 140},
		{"label": _("Container"), "fieldname": "container", "fieldtype": "Link", "options": "Container", "width": 120},
		{"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "options": "currency", "width": 110},
		{"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
	]


def get_conditions(filters):
	conditions = ["1=1"]
	values = {}

	if filters.get("job"):
		conditions.append("e.job = %(job)s")
		values["job"] = filters.get("job")
	if filters.get("cost_type"):
		conditions.append("e.cost_type = %(cost_type)s")
		values["cost_type"] = filters.get("cost_type")
	if filters.get("supplier"):
		conditions.append("e.supplier = %(supplier)s")
		values["supplier"] = filters.get("supplier")
	if filters.get("container"):
		conditions.append("e.container = %(container)s")
		values["container"] = filters.get("container")
	if filters.get("customer"):
		conditions.append("j.customer = %(customer)s")
		values["customer"] = filters.get("customer")
	if filters.get("branch"):
		conditions.append("j.branch = %(branch)s")
		values["branch"] = filters.get("branch")
	if filters.get("company"):
		conditions.append("j.company = %(company)s")
		values["company"] = filters.get("company")
	if filters.get("from_date"):
		conditions.append("e.posting_date >= %(from_date)s")
		values["from_date"] = filters.get("from_date")
	if filters.get("to_date"):
		conditions.append("e.posting_date <= %(to_date)s")
		values["to_date"] = filters.get("to_date")

	return " and ".join(conditions), values


def get_data(filters):
	conditions, values = get_conditions(filters)
	query = f"""
		select
			e.name, e.job, j.customer, j.branch, e.cost_type, e.supplier,
			e.purchase_invoice, e.job_cost_allocation, e.container, e.amount, e.posting_date
		from `tabJob Cost Entry` e
		left join `tabClearing and Forwarding Job` j on j.name = e.job
		where {conditions}
		order by e.posting_date desc
	"""
	return frappe.db.sql(query, values, as_dict=1)


def get_chart(data):
	if not data:
		return None
	totals = {}
	for row in data:
		totals[row.cost_type] = totals.get(row.cost_type, 0) + flt(row.amount)
	return {
		"data": {
			"labels": list(totals.keys()),
			"datasets": [{"name": _("Cost by Type"), "values": list(totals.values())}],
		},
		"type": "pie",
	}


def get_summary(data):
	total = sum([flt(d.amount) for d in data])
	jobs = len(set([d.job for d in data if d.job]))
	suppliers = len(set([d.supplier for d in data if d.supplier]))
	return [
		{"label": _("Total Cost Entries"), "value": len(data), "indicator": "Blue"},
		{"label": _("Total Amount"), "value": frappe.utils.fmt_money(total), "indicator": "Orange"},
		{"label": _("Jobs Covered"), "value": jobs, "indicator": "Blue"},
		{"label": _("Suppliers Involved"), "value": suppliers, "indicator": "Blue"},
	]
