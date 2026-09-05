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
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 130},
		{"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 170},
		{"label": _("Job Count"), "fieldname": "job_count", "fieldtype": "Int", "width": 90},
		{"label": _("Est. Revenue"), "fieldname": "estimated_revenue", "fieldtype": "Currency", "options": "currency", "width": 130},
		{"label": _("Actual Revenue"), "fieldname": "actual_revenue", "fieldtype": "Currency", "options": "currency", "width": 130},
		{"label": _("Actual Cost"), "fieldname": "actual_cost", "fieldtype": "Currency", "options": "currency", "width": 120},
		{"label": _("Gross Profit"), "fieldname": "gross_profit", "fieldtype": "Currency", "options": "currency", "width": 120},
		{"label": _("Avg Margin %"), "fieldname": "avg_margin", "fieldtype": "Percent", "width": 100},
		{"label": _("Billed"), "fieldname": "billed_amount", "fieldtype": "Currency", "options": "currency", "width": 110},
		{"label": _("Outstanding"), "fieldname": "outstanding_amount", "fieldtype": "Currency", "options": "currency", "width": 115},
	]


def get_conditions(filters):
	conditions = ["j.docstatus = 1"]
	values = {}
	for f in ("customer", "branch", "company"):
		if filters.get(f):
			conditions.append(f"j.{f} = %({f})s")
			values[f] = filters.get(f)
	if filters.get("from_date"):
		conditions.append("date(j.creation) >= %(from_date)s")
		values["from_date"] = filters.get("from_date")
	if filters.get("to_date"):
		conditions.append("date(j.creation) <= %(to_date)s")
		values["to_date"] = filters.get("to_date")
	return " and ".join(conditions), values


def get_data(filters):
	conditions, values = get_conditions(filters)
	query = f"""
		select
			j.customer, cust.customer_name,
			count(j.name) as job_count,
			sum(j.estimated_revenue) as estimated_revenue,
			sum(j.actual_revenue) as actual_revenue,
			sum(j.actual_cost) as actual_cost,
			sum(j.gross_profit) as gross_profit,
			sum(j.billed_amount) as billed_amount,
			sum(j.outstanding_amount) as outstanding_amount
		from `tabClearing and Forwarding Job` j
		left join `tabCustomer` cust on cust.name = j.customer
		where {conditions}
		group by j.customer
		order by gross_profit desc
	"""
	data = frappe.db.sql(query, values, as_dict=1)
	for row in data:
		row.avg_margin = (flt(row.gross_profit) / flt(row.actual_revenue) * 100) if row.actual_revenue else 0
	return data


def get_chart(data):
	if not data:
		return None
	top = sorted(data, key=lambda d: flt(d.gross_profit), reverse=True)[:10]
	return {
		"data": {
			"labels": [d.customer_name or d.customer for d in top],
			"datasets": [{"name": _("Gross Profit"), "values": [flt(d.gross_profit) for d in top]}],
		},
		"type": "bar",
		"colors": ["#2e7d32"],
	}


def get_summary(data):
	total_customers = len(data)
	total_profit = sum([flt(d.gross_profit) for d in data])
	total_outstanding = sum([flt(d.outstanding_amount) for d in data])
	total_jobs = sum([d.job_count for d in data])
	return [
		{"label": _("Customers"), "value": total_customers, "indicator": "Blue"},
		{"label": _("Total Jobs"), "value": total_jobs, "indicator": "Blue"},
		{"label": _("Total Gross Profit"), "value": frappe.utils.fmt_money(total_profit), "indicator": "Green" if total_profit >= 0 else "Red"},
		{"label": _("Total Outstanding"), "value": frappe.utils.fmt_money(total_outstanding), "indicator": "Orange"},
	]
