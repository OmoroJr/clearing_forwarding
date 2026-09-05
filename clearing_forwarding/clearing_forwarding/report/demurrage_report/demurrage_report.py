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
		{"label": _("Record"), "fieldname": "name", "fieldtype": "Link", "options": "Demurrage And Detention", "width": 150},
		{"label": _("Job"), "fieldname": "job", "fieldtype": "Link", "options": "Clearing and Forwarding Job", "width": 140},
		{"label": _("Container"), "fieldname": "container", "fieldtype": "Link", "options": "Container", "width": 130},
		{"label": _("Shipping Line"), "fieldname": "shipping_line", "fieldtype": "Link", "options": "Shipping Line", "width": 120},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
		{"label": _("Free Days"), "fieldname": "free_days", "fieldtype": "Int", "width": 80},
		{"label": _("Free Time Start"), "fieldname": "free_time_start", "fieldtype": "Date", "width": 110},
		{"label": _("Free Time End"), "fieldname": "free_time_end", "fieldtype": "Date", "width": 110},
		{"label": _("Actual Return"), "fieldname": "actual_return_date", "fieldtype": "Date", "width": 105},
		{"label": _("Days Overdue"), "fieldname": "days_overdue", "fieldtype": "Int", "width": 100},
		{"label": _("Daily Rate"), "fieldname": "daily_rate", "fieldtype": "Currency", "options": "currency", "width": 100},
		{"label": _("Total Charge"), "fieldname": "total_charge", "fieldtype": "Currency", "options": "currency", "width": 110},
		{"label": _("Customer Charge"), "fieldname": "customer_charge", "fieldtype": "Currency", "options": "currency", "width": 120},
		{"label": _("Supplier Charge"), "fieldname": "supplier_charge", "fieldtype": "Currency", "options": "currency", "width": 120},
	]


def get_conditions(filters):
	conditions = ["1=1"]
	values = {}

	for f in ("job", "container", "shipping_line", "status"):
		if filters.get(f):
			conditions.append(f"d.{f} = %({f})s")
			values[f] = filters.get(f)

	if filters.get("only_overdue"):
		conditions.append("d.days_overdue > 0")

	if filters.get("from_date"):
		conditions.append("d.free_time_start >= %(from_date)s")
		values["from_date"] = filters.get("from_date")
	if filters.get("to_date"):
		conditions.append("d.free_time_start <= %(to_date)s")
		values["to_date"] = filters.get("to_date")

	return " and ".join(conditions), values


def get_data(filters):
	conditions, values = get_conditions(filters)
	query = f"""
		select
			d.name, d.job, d.container, d.shipping_line, d.status, d.free_days,
			d.free_time_start, d.free_time_end, d.actual_return_date, d.days_overdue,
			d.daily_rate, d.total_charge, d.customer_charge, d.supplier_charge
		from `tabDemurrage And Detention` d
		where {conditions}
		order by d.days_overdue desc, d.free_time_end asc
	"""
	return frappe.db.sql(query, values, as_dict=1)


def get_chart(data):
	if not data:
		return None
	counts = {}
	for row in data:
		counts[row.status] = counts.get(row.status, 0) + 1
	return {
		"data": {
			"labels": list(counts.keys()),
			"datasets": [{"name": _("Containers"), "values": list(counts.values())}],
		},
		"type": "donut",
		"colors": ["#c62828", "#ef6c00", "#2e7d32", "#1565c0"],
	}


def get_summary(data):
	overdue = [d for d in data if flt(d.days_overdue) > 0]
	total_charge = sum([flt(d.total_charge) for d in data])
	nearing = len([d for d in data if d.status == "Nearing Expiry"])
	return [
		{"label": _("Containers Tracked"), "value": len(data), "indicator": "Blue"},
		{"label": _("Currently Overdue"), "value": len(overdue), "indicator": "Red" if overdue else "Green"},
		{"label": _("Nearing Expiry"), "value": nearing, "indicator": "Orange" if nearing else "Green"},
		{"label": _("Total Demurrage/Detention Charge"), "value": frappe.utils.fmt_money(total_charge), "indicator": "Orange"},
	]
