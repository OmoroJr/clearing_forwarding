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
		{"label": _("Job"), "fieldname": "name", "fieldtype": "Link", "options": "Clearing and Forwarding Job", "width": 140},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 140},
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 120},
		{"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 160},
		{"label": _("Job Type"), "fieldname": "job_type", "fieldtype": "Data", "width": 130},
		{"label": _("Import/Export"), "fieldname": "import_export", "fieldtype": "Data", "width": 100},
		{"label": _("Mode"), "fieldname": "mode_of_transport", "fieldtype": "Data", "width": 80},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 110},
		{"label": _("Shipping Line"), "fieldname": "shipping_line", "fieldtype": "Link", "options": "Shipping Line", "width": 130},
		{"label": _("Clearing Agent"), "fieldname": "clearing_agent", "fieldtype": "Link", "options": "Clearing Agent", "width": 130},
		{"label": _("Containers"), "fieldname": "container_count", "fieldtype": "Int", "width": 90},
		{"label": _("ETA"), "fieldname": "eta", "fieldtype": "Date", "width": 95},
		{"label": _("ETD"), "fieldname": "etd", "fieldtype": "Date", "width": 95},
		{"label": _("Actual Arrival"), "fieldname": "actual_arrival_date", "fieldtype": "Date", "width": 105},
		{"label": _("Delivery Date"), "fieldname": "delivery_date", "fieldtype": "Date", "width": 105},
		{"label": _("Customs Status"), "fieldname": "customs_status", "fieldtype": "Data", "width": 120},
		{"label": _("Payment Status"), "fieldname": "payment_status", "fieldtype": "Data", "width": 110},
		{"label": _("Outstanding"), "fieldname": "outstanding_amount", "fieldtype": "Currency", "options": "currency", "width": 110},
		{"label": _("Created On"), "fieldname": "creation", "fieldtype": "Date", "width": 100},
	]


def get_conditions(filters):
	conditions = ["j.docstatus < 2"]
	values = {}

	simple_filters = [
		"company", "branch", "customer", "job_type", "import_export",
		"mode_of_transport", "status", "shipping_line", "clearing_agent",
		"payment_status",
	]
	for f in simple_filters:
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
			j.name, j.status, j.customer, cust.customer_name, j.job_type,
			j.import_export, j.mode_of_transport, j.branch, j.shipping_line,
			j.clearing_agent, j.container_count, j.eta, j.etd,
			j.actual_arrival_date, j.delivery_date, j.customs_status,
			j.payment_status, j.outstanding_amount, j.creation
		from `tabClearing and Forwarding Job` j
		left join `tabCustomer` cust on cust.name = j.customer
		where {conditions}
		order by j.creation desc
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
			"datasets": [{"name": _("Jobs"), "values": list(counts.values())}],
		},
		"type": "bar",
		"colors": ["#2e7d32"],
	}


def get_summary(data):
	total = len(data)
	cancelled = len([d for d in data if d.status == "Cancelled"])
	completed = len([d for d in data if d.status == "Completed"])
	open_jobs = total - cancelled - completed
	outstanding = sum([d.outstanding_amount or 0 for d in data])
	return [
		{"label": _("Total Jobs"), "value": total, "indicator": "Blue"},
		{"label": _("Open / In Progress"), "value": open_jobs, "indicator": "Orange"},
		{"label": _("Completed"), "value": completed, "indicator": "Green"},
		{"label": _("Cancelled"), "value": cancelled, "indicator": "Red"},
		{"label": _("Total Outstanding"), "value": frappe.utils.fmt_money(outstanding), "indicator": "Orange"},
	]
