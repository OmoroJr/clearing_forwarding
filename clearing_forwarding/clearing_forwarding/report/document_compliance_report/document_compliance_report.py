# Copyright (c) 2026, Clearing Forwarding and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import date_diff, getdate, nowdate


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
		{"label": _("Document Type"), "fieldname": "document_type", "fieldtype": "Data", "width": 160},
		{"label": _("Document Number"), "fieldname": "document_number", "fieldtype": "Data", "width": 130},
		{"label": _("Issuing Agency"), "fieldname": "issuing_agency", "fieldtype": "Link", "options": "Government Agency", "width": 140},
		{"label": _("Required"), "fieldname": "required", "fieldtype": "Check", "width": 75},
		{"label": _("Received"), "fieldname": "received", "fieldtype": "Check", "width": 75},
		{"label": _("Verified"), "fieldname": "verified", "fieldtype": "Check", "width": 75},
		{"label": _("Issue Date"), "fieldname": "issue_date", "fieldtype": "Date", "width": 95},
		{"label": _("Expiry Date"), "fieldname": "expiry_date", "fieldtype": "Date", "width": 95},
		{"label": _("Days to Expiry"), "fieldname": "days_to_expiry", "fieldtype": "Int", "width": 105},
		{"label": _("Compliance Status"), "fieldname": "compliance_status", "fieldtype": "Data", "width": 150},
	]


def get_conditions(filters):
	conditions = ["j.docstatus < 2"]
	values = {}

	if filters.get("job"):
		conditions.append("cd.parent = %(job)s")
		values["job"] = filters.get("job")
	if filters.get("customer"):
		conditions.append("j.customer = %(customer)s")
		values["customer"] = filters.get("customer")
	if filters.get("branch"):
		conditions.append("j.branch = %(branch)s")
		values["branch"] = filters.get("branch")
	if filters.get("document_type"):
		conditions.append("cd.document_type = %(document_type)s")
		values["document_type"] = filters.get("document_type")
	if filters.get("issuing_agency"):
		conditions.append("cd.issuing_agency = %(issuing_agency)s")
		values["issuing_agency"] = filters.get("issuing_agency")

	return " and ".join(conditions), values


def get_data(filters):
	conditions, values = get_conditions(filters)
	query = f"""
		select
			cd.parent as job, j.customer, j.status as job_status,
			cd.document_type, cd.document_number, cd.issuing_agency,
			cd.required, cd.received, cd.verified, cd.issue_date, cd.expiry_date
		from `tabCF Job Document` cd
		inner join `tabClearing and Forwarding Job` j on j.name = cd.parent
		where {conditions}
		order by j.name
	"""
	data = frappe.db.sql(query, values, as_dict=1)

	today = getdate(nowdate())
	expiring_within = filters.get("expiring_within_days")
	filtered = []

	for row in data:
		row.days_to_expiry = date_diff(row.expiry_date, today) if row.expiry_date else None
		row.compliance_status = get_compliance_status(row, today)

		if filters.get("only_missing") and not (row.required and not row.received):
			continue
		if filters.get("only_unverified") and not (row.received and not row.verified):
			continue
		if expiring_within:
			if row.days_to_expiry is None or not (0 <= row.days_to_expiry <= int(expiring_within)):
				continue

		filtered.append(row)

	return filtered


def get_compliance_status(row, today):
	if row.expiry_date and getdate(row.expiry_date) < today:
		return _("Expired")
	if row.required and not row.received:
		return _("Missing")
	if row.received and not row.verified:
		return _("Pending Verification")
	if row.expiry_date and 0 <= date_diff(row.expiry_date, today) <= 14:
		return _("Expiring Soon")
	if row.verified:
		return _("Verified")
	if not row.required:
		return _("Not Required")
	return _("Pending")


def get_chart(data):
	if not data:
		return None
	counts = {}
	for row in data:
		counts[row.compliance_status] = counts.get(row.compliance_status, 0) + 1
	return {
		"data": {
			"labels": list(counts.keys()),
			"datasets": [{"name": _("Documents"), "values": list(counts.values())}],
		},
		"type": "donut",
		"colors": ["#c62828", "#ef6c00", "#f9a825", "#2e7d32", "#9e9e9e"],
	}


def get_summary(data):
	missing = len([d for d in data if d.compliance_status == _("Missing")])
	unverified = len([d for d in data if d.compliance_status == _("Pending Verification")])
	expiring = len([d for d in data if d.compliance_status == _("Expiring Soon")])
	expired = len([d for d in data if d.compliance_status == _("Expired")])
	return [
		{"label": _("Total Document Rows"), "value": len(data), "indicator": "Blue"},
		{"label": _("Missing"), "value": missing, "indicator": "Red" if missing else "Green"},
		{"label": _("Pending Verification"), "value": unverified, "indicator": "Orange" if unverified else "Green"},
		{"label": _("Expiring Soon"), "value": expiring, "indicator": "Orange" if expiring else "Green"},
		{"label": _("Expired"), "value": expired, "indicator": "Red" if expired else "Green"},
	]
