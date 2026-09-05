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
		{"label": _("Job"), "fieldname": "job", "fieldtype": "Link", "options": "Clearing and Forwarding Job", "width": 140},
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 120},
		{"label": _("Job Status"), "fieldname": "job_status", "fieldtype": "Data", "width": 130},
		{"label": _("Agency"), "fieldname": "agency", "fieldtype": "Link", "options": "Government Agency", "width": 160},
		{"label": _("Required"), "fieldname": "required", "fieldtype": "Check", "width": 80},
		{"label": _("Clearance Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
		{"label": _("Reference Number"), "fieldname": "reference_number", "fieldtype": "Data", "width": 130},
		{"label": _("Date Cleared"), "fieldname": "date_cleared", "fieldtype": "Date", "width": 105},
	]


def get_conditions(filters):
	conditions = ["j.docstatus < 2"]
	values = {}

	if filters.get("job"):
		conditions.append("ac.parent = %(job)s")
		values["job"] = filters.get("job")
	if filters.get("customer"):
		conditions.append("j.customer = %(customer)s")
		values["customer"] = filters.get("customer")
	if filters.get("agency"):
		conditions.append("ac.agency = %(agency)s")
		values["agency"] = filters.get("agency")
	if filters.get("status"):
		conditions.append("ac.status = %(status)s")
		values["status"] = filters.get("status")

	return " and ".join(conditions), values


def get_data(filters):
	conditions, values = get_conditions(filters)
	query = f"""
		select
			ac.parent as job, j.customer, j.status as job_status,
			ac.agency, ac.required, ac.status, ac.reference_number, ac.date_cleared
		from `tabCF Job Agency Clearance` ac
		inner join `tabClearing and Forwarding Job` j on j.name = ac.parent
		where {conditions}
		order by ac.parent, ac.agency
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
			"datasets": [{"name": _("Clearances"), "values": list(counts.values())}],
		},
		"type": "donut",
		"colors": ["#f9a825", "#1565c0", "#2e7d32", "#c62828"],
	}


def get_summary(data):
	pending = len([d for d in data if d.status == "Pending"])
	in_progress = len([d for d in data if d.status == "In Progress"])
	cleared = len([d for d in data if d.status == "Cleared"])
	rejected = len([d for d in data if d.status == "Rejected"])
	return [
		{"label": _("Total Clearances"), "value": len(data), "indicator": "Blue"},
		{"label": _("Pending"), "value": pending, "indicator": "Orange" if pending else "Green"},
		{"label": _("In Progress"), "value": in_progress, "indicator": "Blue"},
		{"label": _("Cleared"), "value": cleared, "indicator": "Green"},
		{"label": _("Rejected"), "value": rejected, "indicator": "Red" if rejected else "Green"},
	]
