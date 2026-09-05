# Copyright (c) 2026, Clearing Forwarding and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import date_diff, flt, getdate, nowdate


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	summary = get_summary(data)
	return columns, data, None, chart, summary


def get_columns():
	return [
		{"label": _("Job"), "fieldname": "name", "fieldtype": "Link", "options": "Clearing and Forwarding Job", "width": 140},
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 120},
		{"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 160},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 100},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
		{"label": _("Payment Status"), "fieldname": "payment_status", "fieldtype": "Data", "width": 110},
		{"label": _("Delivery Date"), "fieldname": "delivery_date", "fieldtype": "Date", "width": 105},
		{"label": _("Days Outstanding"), "fieldname": "days_outstanding", "fieldtype": "Int", "width": 115},
		{"label": _("Billed Amount"), "fieldname": "billed_amount", "fieldtype": "Currency", "options": "currency", "width": 115},
		{"label": _("Outstanding Amount"), "fieldname": "outstanding_amount", "fieldtype": "Currency", "options": "currency", "width": 130},
	]


def get_conditions(filters):
	conditions = ["j.docstatus = 1", "j.outstanding_amount > 0"]
	values = {}

	for f in ("customer", "branch", "company", "payment_status"):
		if filters.get(f):
			conditions.append(f"j.{f} = %({f})s")
			values[f] = filters.get(f)

	if filters.get("from_date"):
		conditions.append("j.delivery_date >= %(from_date)s")
		values["from_date"] = filters.get("from_date")
	if filters.get("to_date"):
		conditions.append("j.delivery_date <= %(to_date)s")
		values["to_date"] = filters.get("to_date")

	return " and ".join(conditions), values


def get_data(filters):
	conditions, values = get_conditions(filters)
	query = f"""
		select
			j.name, j.customer, cust.customer_name, j.branch, j.status,
			j.payment_status, j.delivery_date, j.billed_amount, j.outstanding_amount
		from `tabClearing and Forwarding Job` j
		left join `tabCustomer` cust on cust.name = j.customer
		where {conditions}
		order by j.outstanding_amount desc
	"""
	data = frappe.db.sql(query, values, as_dict=1)

	today = getdate(nowdate())
	min_outstanding = flt(filters.get("min_outstanding"))
	result = []
	for row in data:
		row.days_outstanding = date_diff(today, row.delivery_date) if row.delivery_date else None
		if min_outstanding and flt(row.outstanding_amount) < min_outstanding:
			continue
		result.append(row)
	return result


def get_chart(data):
	if not data:
		return None
	totals = {}
	for row in data:
		key = row.customer_name or row.customer
		totals[key] = totals.get(key, 0) + flt(row.outstanding_amount)
	top = dict(sorted(totals.items(), key=lambda x: x[1], reverse=True)[:10])
	return {
		"data": {
			"labels": list(top.keys()),
			"datasets": [{"name": _("Outstanding"), "values": list(top.values())}],
		},
		"type": "bar",
		"colors": ["#c62828"],
	}


def get_summary(data):
	total_outstanding = sum([flt(d.outstanding_amount) for d in data])
	total_billed = sum([flt(d.billed_amount) for d in data])
	over_30 = len([d for d in data if (d.days_outstanding or 0) > 30])
	customers = len(set([d.customer for d in data]))
	return [
		{"label": _("Jobs with Outstanding Balance"), "value": len(data), "indicator": "Orange"},
		{"label": _("Customers Affected"), "value": customers, "indicator": "Blue"},
		{"label": _("Total Outstanding"), "value": frappe.utils.fmt_money(total_outstanding), "indicator": "Red"},
		{"label": _("Total Billed"), "value": frappe.utils.fmt_money(total_billed), "indicator": "Blue"},
		{"label": _("Overdue > 30 Days Since Delivery"), "value": over_30, "indicator": "Red" if over_30 else "Green"},
	]
