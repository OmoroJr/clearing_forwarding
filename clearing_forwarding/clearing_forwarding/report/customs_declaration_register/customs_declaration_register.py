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
		{"label": _("Declaration"), "fieldname": "name", "fieldtype": "Link", "options": "Customs Declaration", "width": 150},
		{"label": _("Job"), "fieldname": "job", "fieldtype": "Link", "options": "Clearing and Forwarding Job", "width": 140},
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 120},
		{"label": _("Import/Export"), "fieldname": "import_export", "fieldtype": "Data", "width": 100},
		{"label": _("Declaration No."), "fieldname": "declaration_number", "fieldtype": "Data", "width": 130},
		{"label": _("Entry No."), "fieldname": "entry_number", "fieldtype": "Data", "width": 110},
		{"label": _("Customs Station"), "fieldname": "customs_station", "fieldtype": "Link", "options": "Government Agency", "width": 140},
		{"label": _("Declaration Date"), "fieldname": "declaration_date", "fieldtype": "Date", "width": 115},
		{"label": _("Customs Value"), "fieldname": "customs_value", "fieldtype": "Currency", "options": "currency", "width": 115},
		{"label": _("Duty"), "fieldname": "duty", "fieldtype": "Currency", "options": "currency", "width": 95},
		{"label": _("VAT"), "fieldname": "vat", "fieldtype": "Currency", "options": "currency", "width": 90},
		{"label": _("Excise"), "fieldname": "excise", "fieldtype": "Currency", "options": "currency", "width": 95},
		{"label": _("IDF"), "fieldname": "idf", "fieldtype": "Currency", "options": "currency", "width": 90},
		{"label": _("RDL"), "fieldname": "rdl", "fieldtype": "Currency", "options": "currency", "width": 90},
		{"label": _("Other Taxes"), "fieldname": "other_taxes", "fieldtype": "Currency", "options": "currency", "width": 105},
		{"label": _("Total Taxes"), "fieldname": "total_taxes", "fieldtype": "Currency", "options": "currency", "width": 110},
		{"label": _("Assessment Status"), "fieldname": "assessment_status", "fieldtype": "Data", "width": 130},
		{"label": _("Clearance Status"), "fieldname": "clearance_status", "fieldtype": "Data", "width": 120},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
		{"label": _("Payment Date"), "fieldname": "payment_date", "fieldtype": "Date", "width": 105},
	]


def get_conditions(filters):
	conditions = ["cd.docstatus < 2"]
	values = {}

	for f in ("job", "customer", "status", "assessment_status", "clearance_status", "customs_station", "import_export"):
		if filters.get(f):
			conditions.append(f"cd.{f} = %({f})s")
			values[f] = filters.get(f)

	if filters.get("from_date"):
		conditions.append("cd.declaration_date >= %(from_date)s")
		values["from_date"] = filters.get("from_date")
	if filters.get("to_date"):
		conditions.append("cd.declaration_date <= %(to_date)s")
		values["to_date"] = filters.get("to_date")

	return " and ".join(conditions), values


def get_data(filters):
	conditions, values = get_conditions(filters)
	query = f"""
		select
			cd.name, cd.job, cd.customer, cd.import_export, cd.declaration_number,
			cd.entry_number, cd.customs_station, cd.declaration_date, cd.customs_value,
			cd.duty, cd.vat, cd.excise, cd.idf, cd.rdl, cd.other_taxes, cd.total_taxes,
			cd.assessment_status, cd.clearance_status, cd.status, cd.payment_date
		from `tabCustoms Declaration` cd
		where {conditions}
		order by cd.declaration_date desc
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
			"datasets": [{"name": _("Declarations"), "values": list(counts.values())}],
		},
		"type": "donut",
	}


def get_summary(data):
	total_taxes = sum([flt(d.total_taxes) for d in data])
	pending_assessment = len([d for d in data if d.assessment_status == "Pending"])
	pending_payment = len([d for d in data if d.status == "Payment Pending"])
	return [
		{"label": _("Declarations"), "value": len(data), "indicator": "Blue"},
		{"label": _("Total Taxes Assessed"), "value": frappe.utils.fmt_money(total_taxes), "indicator": "Orange"},
		{"label": _("Pending Assessment"), "value": pending_assessment, "indicator": "Orange" if pending_assessment else "Green"},
		{"label": _("Duty Payment Pending"), "value": pending_payment, "indicator": "Red" if pending_payment else "Green"},
	]
