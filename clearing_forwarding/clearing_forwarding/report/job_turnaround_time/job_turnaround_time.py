# Copyright (c) 2026, Clearing Forwarding and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import date_diff


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
		{"label": _("Job Type"), "fieldname": "job_type", "fieldtype": "Data", "width": 130},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 100},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 130},
		{"label": _("Created On"), "fieldname": "created_on", "fieldtype": "Date", "width": 100},
		{"label": _("ETA"), "fieldname": "eta", "fieldtype": "Date", "width": 95},
		{"label": _("Actual Arrival"), "fieldname": "actual_arrival_date", "fieldtype": "Date", "width": 110},
		{"label": _("Delivery Date"), "fieldname": "delivery_date", "fieldtype": "Date", "width": 105},
		{"label": _("Turnaround Days"), "fieldname": "turnaround_days", "fieldtype": "Int", "width": 125, "description": _("Job creation to delivery")},
		{"label": _("Arrival to Delivery"), "fieldname": "arrival_to_delivery_days", "fieldtype": "Int", "width": 135, "description": _("Actual arrival to delivery")},
		{"label": _("ETA Accuracy (Days)"), "fieldname": "eta_variance_days", "fieldtype": "Int", "width": 140, "description": _("Actual arrival minus ETA; positive = late")},
	]


def get_conditions(filters):
	conditions = ["j.docstatus < 2"]
	values = {}

	for f in ("branch", "customer", "company", "job_type"):
		if filters.get(f):
			conditions.append(f"j.{f} = %({f})s")
			values[f] = filters.get(f)

	if filters.get("only_completed"):
		conditions.append("j.delivery_date is not null")

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
			j.name, j.customer, j.job_type, j.branch, j.status,
			date(j.creation) as created_on, j.eta, j.actual_arrival_date, j.delivery_date
		from `tabClearing and Forwarding Job` j
		where {conditions}
		order by j.creation desc
	"""
	data = frappe.db.sql(query, values, as_dict=1)

	for row in data:
		row.turnaround_days = (
			date_diff(row.delivery_date, row.created_on) if row.delivery_date and row.created_on else None
		)
		row.arrival_to_delivery_days = (
			date_diff(row.delivery_date, row.actual_arrival_date)
			if row.delivery_date and row.actual_arrival_date else None
		)
		row.eta_variance_days = (
			date_diff(row.actual_arrival_date, row.eta) if row.actual_arrival_date and row.eta else None
		)

	return data


def get_chart(data):
	completed = [d for d in data if d.turnaround_days is not None]
	if not completed:
		return None
	totals = {}
	counts = {}
	for row in completed:
		key = row.job_type or _("Unspecified")
		totals[key] = totals.get(key, 0) + row.turnaround_days
		counts[key] = counts.get(key, 0) + 1
	avgs = {k: round(totals[k] / counts[k], 1) for k in totals}
	return {
		"data": {
			"labels": list(avgs.keys()),
			"datasets": [{"name": _("Avg. Turnaround Days"), "values": list(avgs.values())}],
		},
		"type": "bar",
		"colors": ["#1565c0"],
	}


def get_summary(data):
	completed = [d for d in data if d.turnaround_days is not None]
	if not completed:
		return [{"label": _("Jobs with Turnaround Data"), "value": 0, "indicator": "Blue"}]
	days = [d.turnaround_days for d in completed]
	avg_days = sum(days) / len(days)
	return [
		{"label": _("Jobs with Turnaround Data"), "value": len(completed), "indicator": "Blue"},
		{"label": _("Avg. Turnaround (Days)"), "value": f"{avg_days:.1f}", "indicator": "Blue"},
		{"label": _("Fastest (Days)"), "value": min(days), "indicator": "Green"},
		{"label": _("Slowest (Days)"), "value": max(days), "indicator": "Red"},
	]
