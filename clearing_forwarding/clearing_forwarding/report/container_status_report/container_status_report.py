# Copyright (c) 2026, Clearing Forwarding and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

CLOSED_STATUSES = ("Empty Returned",)


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	summary = get_summary(data)
	return columns, data, None, chart, summary


def get_columns():
	return [
		{"label": _("Container"), "fieldname": "name", "fieldtype": "Link", "options": "Container", "width": 130},
		{"label": _("Job"), "fieldname": "job", "fieldtype": "Link", "options": "Clearing and Forwarding Job", "width": 140},
		{"label": _("Shipping Line"), "fieldname": "shipping_line", "fieldtype": "Link", "options": "Shipping Line", "width": 120},
		{"label": _("Type"), "fieldname": "container_type", "fieldtype": "Data", "width": 110},
		{"label": _("Owner Type"), "fieldname": "owner_type", "fieldtype": "Data", "width": 120},
		{"label": _("Status"), "fieldname": "container_status", "fieldtype": "Data", "width": 110},
		{"label": _("Current Location"), "fieldname": "current_location", "fieldtype": "Data", "width": 140},
		{"label": _("Seal Number"), "fieldname": "seal_number", "fieldtype": "Data", "width": 110},
		{"label": _("Gross Wt (kg)"), "fieldname": "gross_weight", "fieldtype": "Float", "width": 100},
		{"label": _("Tare Wt (kg)"), "fieldname": "tare_weight", "fieldtype": "Float", "width": 100},
		{"label": _("Cargo Wt (kg)"), "fieldname": "cargo_weight", "fieldtype": "Float", "width": 105},
		{"label": _("Arrival Date"), "fieldname": "arrival_date", "fieldtype": "Date", "width": 100},
		{"label": _("Release Date"), "fieldname": "release_date", "fieldtype": "Date", "width": 100},
		{"label": _("Gate Out Date"), "fieldname": "gate_out_date", "fieldtype": "Date", "width": 105},
		{"label": _("Empty Return Date"), "fieldname": "empty_return_date", "fieldtype": "Date", "width": 130},
		{"label": _("Demurrage Status"), "fieldname": "demurrage_status", "fieldtype": "Data", "width": 130},
	]


def get_conditions(filters):
	conditions = ["1=1"]
	values = {}

	for f in ("job", "shipping_line", "container_type", "container_status", "owner_type", "demurrage_status"):
		if filters.get(f):
			conditions.append(f"c.{f} = %({f})s")
			values[f] = filters.get(f)

	if filters.get("only_active"):
		placeholders = ", ".join([f"%(closed_{i})s" for i in range(len(CLOSED_STATUSES))])
		conditions.append(f"(c.container_status is null or c.container_status not in ({placeholders}))")
		for i, s in enumerate(CLOSED_STATUSES):
			values[f"closed_{i}"] = s

	return " and ".join(conditions), values


def get_data(filters):
	conditions, values = get_conditions(filters)
	query = f"""
		select
			c.name, c.job, c.shipping_line, c.container_type, c.owner_type,
			c.container_status, c.current_location, c.seal_number,
			c.gross_weight, c.tare_weight, c.cargo_weight,
			c.arrival_date, c.release_date, c.gate_out_date, c.empty_return_date,
			c.demurrage_status
		from `tabContainer` c
		where {conditions}
		order by c.arrival_date desc
	"""
	return frappe.db.sql(query, values, as_dict=1)


def get_chart(data):
	if not data:
		return None
	counts = {}
	for row in data:
		key = row.container_status or _("Not Set")
		counts[key] = counts.get(key, 0) + 1
	return {
		"data": {
			"labels": list(counts.keys()),
			"datasets": [{"name": _("Containers"), "values": list(counts.values())}],
		},
		"type": "bar",
		"colors": ["#1565c0"],
	}


def get_summary(data):
	active = len([d for d in data if d.container_status not in CLOSED_STATUSES])
	overdue_demurrage = len([d for d in data if d.demurrage_status == "Overdue"])
	total_cargo_weight = sum([flt(d.cargo_weight) for d in data])
	return [
		{"label": _("Containers"), "value": len(data), "indicator": "Blue"},
		{"label": _("Active (Not Yet Returned)"), "value": active, "indicator": "Blue"},
		{"label": _("Overdue on Demurrage"), "value": overdue_demurrage, "indicator": "Red" if overdue_demurrage else "Green"},
		{"label": _("Total Cargo Weight (kg)"), "value": f"{total_cargo_weight:,.0f}", "indicator": "Blue"},
	]
