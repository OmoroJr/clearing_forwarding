# Copyright (c) 2026, Clearing Forwarding and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import date_diff, flt, getdate, nowdate

# Statuses at or beyond "Delivered" in the Job status lifecycle - i.e. jobs
# where operational work is essentially done and billing should follow.
# Kept as a local literal (rather than importing JOB_STATUS_ORDER from the
# Job controller) to keep this report's only dependency on the database.
BILLABLE_STAGE_STATUSES = [
	"Delivered", "Billing Pending", "Billed", "Payment Pending", "Completed",
]


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
		{"label": _("Job Type"), "fieldname": "job_type", "fieldtype": "Data", "width": 120},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 130},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 100},
		{"label": _("Delivery Date"), "fieldname": "delivery_date", "fieldtype": "Date", "width": 105},
		{"label": _("Days Since Delivery"), "fieldname": "days_since_delivery", "fieldtype": "Int", "width": 130},
		{"label": _("Estimated Revenue"), "fieldname": "estimated_revenue", "fieldtype": "Currency", "options": "currency", "width": 130},
		{"label": _("Actual Revenue"), "fieldname": "actual_revenue", "fieldtype": "Currency", "options": "currency", "width": 120},
		{"label": _("Actual Cost"), "fieldname": "actual_cost", "fieldtype": "Currency", "options": "currency", "width": 110},
		{"label": _("Gross Profit"), "fieldname": "gross_profit", "fieldtype": "Currency", "options": "currency", "width": 110},
	]


def get_conditions(filters):
	conditions = ["j.docstatus = 1", "j.payment_status = 'Not Billed'"]
	values = {}

	for f in ("branch", "customer", "company", "job_type"):
		if filters.get(f):
			conditions.append(f"j.{f} = %({f})s")
			values[f] = filters.get(f)

	if filters.get("only_delivered_or_later"):
		placeholders = ", ".join([f"%(status_{i})s" for i in range(len(BILLABLE_STAGE_STATUSES))])
		conditions.append(f"j.status in ({placeholders})")
		for i, status in enumerate(BILLABLE_STAGE_STATUSES):
			values[f"status_{i}"] = status

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
			j.name, j.customer, cust.customer_name, j.job_type, j.status, j.branch,
			j.delivery_date, j.estimated_revenue, j.actual_revenue, j.actual_cost,
			j.gross_profit
		from `tabClearing and Forwarding Job` j
		left join `tabCustomer` cust on cust.name = j.customer
		where {conditions}
		order by j.delivery_date asc
	"""
	data = frappe.db.sql(query, values, as_dict=1)

	today = getdate(nowdate())
	min_days = filters.get("min_days_since_delivery")
	result = []
	for row in data:
		row.days_since_delivery = date_diff(today, row.delivery_date) if row.delivery_date else None
		if min_days and (row.days_since_delivery is None or row.days_since_delivery < int(min_days)):
			continue
		result.append(row)
	return result


def get_chart(data):
	if not data:
		return None
	counts = {}
	for row in data:
		counts[row.status] = counts.get(row.status, 0) + 1
	return {
		"data": {
			"labels": list(counts.keys()),
			"datasets": [{"name": _("Unbilled Jobs"), "values": list(counts.values())}],
		},
		"type": "bar",
		"colors": ["#ef6c00"],
	}


def get_summary(data):
	total_revenue_at_risk = sum([flt(d.estimated_revenue) for d in data])
	overdue_delivery = len([d for d in data if (d.days_since_delivery or 0) > 14])
	return [
		{"label": _("Unbilled Jobs"), "value": len(data), "indicator": "Orange"},
		{"label": _("Estimated Revenue Not Yet Billed"), "value": frappe.utils.fmt_money(total_revenue_at_risk), "indicator": "Orange"},
		{"label": _("Delivered > 14 Days Ago, Still Unbilled"), "value": overdue_delivery, "indicator": "Red" if overdue_delivery else "Green"},
	]
