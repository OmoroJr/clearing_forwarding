# Copyright (c) 2026, Clearing Forwarding and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	summary = get_summary(data)
	return columns, data, None, chart, summary


def get_columns():
	return [
		{"label": _("Container"), "fieldname": "container", "fieldtype": "Link", "options": "Container", "width": 130},
		{"label": _("Job"), "fieldname": "job", "fieldtype": "Link", "options": "Clearing and Forwarding Job", "width": 140},
		{"label": _("Date/Time"), "fieldname": "date_time", "fieldtype": "Datetime", "width": 145},
		{"label": _("Previous Location"), "fieldname": "previous_location", "fieldtype": "Data", "width": 150},
		{"label": _("New Location"), "fieldname": "new_location", "fieldtype": "Data", "width": 150},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 110},
		{"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Link", "options": "Vehicle", "width": 120},
		{"label": _("Driver"), "fieldname": "driver", "fieldtype": "Link", "options": "Driver", "width": 120},
		{"label": _("Reference"), "fieldname": "reference", "fieldtype": "Data", "width": 130},
	]


def get_conditions(filters):
	conditions = ["1=1"]
	values = {}

	for f in ("container", "status", "vehicle", "driver"):
		if filters.get(f):
			conditions.append(f"m.{f} = %({f})s")
			values[f] = filters.get(f)

	if filters.get("job"):
		conditions.append("c.job = %(job)s")
		values["job"] = filters.get("job")

	if filters.get("from_date"):
		conditions.append("m.date_time >= %(from_date)s")
		values["from_date"] = filters.get("from_date")
	if filters.get("to_date"):
		conditions.append("m.date_time <= %(to_date)s")
		values["to_date"] = filters.get("to_date")

	return " and ".join(conditions), values


def get_data(filters):
	conditions, values = get_conditions(filters)
	query = f"""
		select
			m.container, c.job, m.date_time, m.previous_location, m.new_location,
			m.status, m.vehicle, m.driver, m.reference
		from `tabContainer Movement Log` m
		left join `tabContainer` c on c.name = m.container
		where {conditions}
		order by m.date_time desc
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
			"datasets": [{"name": _("Movements"), "values": list(counts.values())}],
		},
		"type": "bar",
		"colors": ["#1565c0"],
	}


def get_summary(data):
	containers = len(set([d.container for d in data if d.container]))
	return [
		{"label": _("Movement Records"), "value": len(data), "indicator": "Blue"},
		{"label": _("Distinct Containers"), "value": containers, "indicator": "Blue"},
	]
