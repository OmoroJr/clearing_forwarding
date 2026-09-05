# Copyright (c) 2026, Clearing Forwarding and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

COST_TYPES = [
	"Customs Duty", "Port Charges", "Shipping Line Charges", "Freight", "Transport",
	"Fuel", "Handling", "Storage", "Demurrage", "Detention", "Documentation",
	"Clearing Agent", "Inspection", "Warehousing",
]


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	summary = get_summary(data)
	return columns, data, None, chart, summary


def get_columns():
	columns = [
		{"label": _("Job"), "fieldname": "job", "fieldtype": "Link", "options": "Clearing and Forwarding Job", "width": 140},
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 120},
		{"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 150},
		{"label": _("Job Type"), "fieldname": "job_type", "fieldtype": "Data", "width": 120},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 130},
		{"label": _("BL Number"), "fieldname": "bl_number", "fieldtype": "Data", "width": 110},
		{"label": _("Container"), "fieldname": "container", "fieldtype": "Data", "width": 110},
		{"label": _("Est. Revenue"), "fieldname": "estimated_revenue", "fieldtype": "Currency", "options": "currency", "width": 110},
		{"label": _("Est. Cost"), "fieldname": "estimated_cost", "fieldtype": "Currency", "options": "currency", "width": 110},
	]
	for ct in COST_TYPES:
		columns.append({
			"label": ct, "fieldname": ct.lower().replace(" ", "_"),
			"fieldtype": "Currency", "options": "currency", "width": 95,
		})
	columns += [
		{"label": _("Other Cost"), "fieldname": "other_cost", "fieldtype": "Currency", "options": "currency", "width": 100},
		{"label": _("Revenue"), "fieldname": "revenue", "fieldtype": "Currency", "options": "currency", "width": 110},
		{"label": _("Total Cost"), "fieldname": "total_cost", "fieldtype": "Currency", "options": "currency", "width": 110},
		{"label": _("Gross Profit"), "fieldname": "gross_profit", "fieldtype": "Currency", "options": "currency", "width": 110},
		{"label": _("Margin %"), "fieldname": "margin_percent", "fieldtype": "Percent", "width": 90},
		{"label": _("Cost Variance"), "fieldname": "cost_variance", "fieldtype": "Currency", "options": "currency", "width": 110},
		{"label": _("Revenue Variance"), "fieldname": "revenue_variance", "fieldtype": "Currency", "options": "currency", "width": 120},
	]
	return columns


def get_conditions(filters):
	conditions = ["j.docstatus < 2"]
	values = {}

	if filters.get("only_submitted"):
		conditions[0] = "j.docstatus = 1"

	for f in ("customer", "job", "branch", "company", "job_type", "status"):
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
	jobs = frappe.db.sql(f"""
		select j.name, j.customer, cust.customer_name, j.job_type, j.status,
		       j.bill_of_lading_number, j.container_number,
		       j.estimated_revenue, j.estimated_cost, j.actual_revenue, j.actual_cost,
		       j.gross_profit, j.actual_margin_percent, j.cost_variance, j.revenue_variance
		from `tabClearing and Forwarding Job` j
		left join `tabCustomer` cust on cust.name = j.customer
		where {conditions}
		order by j.creation desc
	""", values, as_dict=1)

	if not jobs:
		return []

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
			"customer_name": j.customer_name,
			"job_type": j.job_type,
			"status": j.status,
			"bl_number": j.bill_of_lading_number,
			"container": j.container_number,
			"estimated_revenue": j.estimated_revenue or 0,
			"estimated_cost": j.estimated_cost or 0,
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
		row["cost_variance"] = j.cost_variance or 0
		row["revenue_variance"] = j.revenue_variance or 0
		data.append(row)

	return data


def get_chart(data):
	if not data:
		return None
	top = sorted(data, key=lambda d: flt(d["gross_profit"]), reverse=True)[:10]
	return {
		"data": {
			"labels": [d["job"] for d in top],
			"datasets": [{"name": _("Gross Profit"), "values": [flt(d["gross_profit"]) for d in top]}],
		},
		"type": "bar",
		"colors": ["#2e7d32"],
	}


def get_summary(data):
	total_rev = sum([flt(d["revenue"]) for d in data])
	total_cost = sum([flt(d["total_cost"]) for d in data])
	total_profit = sum([flt(d["gross_profit"]) for d in data])
	avg_margin = (total_profit / total_rev * 100) if total_rev else 0
	loss_making = len([d for d in data if flt(d["gross_profit"]) < 0])
	return [
		{"label": _("Total Actual Revenue"), "value": frappe.utils.fmt_money(total_rev), "indicator": "Blue"},
		{"label": _("Total Actual Cost"), "value": frappe.utils.fmt_money(total_cost), "indicator": "Orange"},
		{"label": _("Total Gross Profit"), "value": frappe.utils.fmt_money(total_profit), "indicator": "Green" if total_profit >= 0 else "Red"},
		{"label": _("Avg. Margin %"), "value": f"{avg_margin:.1f}%", "indicator": "Blue"},
		{"label": _("Loss-Making Jobs"), "value": loss_making, "indicator": "Red" if loss_making else "Green"},
	]
