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
		{"label": _("Incident"), "fieldname": "name", "fieldtype": "Link", "options": "Shipment Incident", "width": 150},
		{"label": _("Job"), "fieldname": "job", "fieldtype": "Link", "options": "Clearing and Forwarding Job", "width": 140},
		{"label": _("Container"), "fieldname": "container", "fieldtype": "Link", "options": "Container", "width": 120},
		{"label": _("Incident Type"), "fieldname": "incident_type", "fieldtype": "Data", "width": 150},
		{"label": _("Severity"), "fieldname": "severity", "fieldtype": "Data", "width": 90},
		{"label": _("Date/Time"), "fieldname": "date_time", "fieldtype": "Datetime", "width": 140},
		{"label": _("Responsible Person"), "fieldname": "responsible_person", "fieldtype": "Link", "options": "User", "width": 150},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": _("Description"), "fieldname": "description", "fieldtype": "Small Text", "width": 220},
	]


def get_conditions(filters):
	conditions = ["1=1"]
	values = {}

	for f in ("job", "container", "incident_type", "severity", "status", "responsible_person"):
		if filters.get(f):
			conditions.append(f"i.{f} = %({f})s")
			values[f] = filters.get(f)

	if filters.get("from_date"):
		conditions.append("i.date_time >= %(from_date)s")
		values["from_date"] = filters.get("from_date")
	if filters.get("to_date"):
		conditions.append("i.date_time <= %(to_date)s")
		values["to_date"] = filters.get("to_date")

	return " and ".join(conditions), values


def get_data(filters):
	conditions, values = get_conditions(filters)
	query = f"""
		select
			i.name, i.job, i.container, i.incident_type, i.severity, i.date_time,
			i.responsible_person, i.status, i.description
		from `tabShipment Incident` i
		where {conditions}
		order by i.date_time desc
	"""
	return frappe.db.sql(query, values, as_dict=1)


def get_chart(data):
	if not data:
		return None
	counts = {}
	for row in data:
		counts[row.incident_type] = counts.get(row.incident_type, 0) + 1
	return {
		"data": {
			"labels": list(counts.keys()),
			"datasets": [{"name": _("Incidents"), "values": list(counts.values())}],
		},
		"type": "bar",
		"colors": ["#c62828"],
	}


def get_summary(data):
	open_count = len([d for d in data if d.status in ("Open", "In Progress")])
	critical = len([d for d in data if d.severity == "Critical"])
	high = len([d for d in data if d.severity == "High"])
	return [
		{"label": _("Total Incidents"), "value": len(data), "indicator": "Blue"},
		{"label": _("Open / In Progress"), "value": open_count, "indicator": "Orange" if open_count else "Green"},
		{"label": _("Critical"), "value": critical, "indicator": "Red" if critical else "Green"},
		{"label": _("High Severity"), "value": high, "indicator": "Orange" if high else "Green"},
	]
