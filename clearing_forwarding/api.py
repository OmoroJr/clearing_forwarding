import frappe
from frappe import _


@frappe.whitelist()
def get_job_status(job):
	if not frappe.has_permission("Clearing and Forwarding Job", "read", job):
		frappe.throw(_("Not permitted"), frappe.PermissionError)
	return frappe.db.get_value(
		"Clearing and Forwarding Job", job,
		["name", "status", "job_type", "customer", "eta", "etd", "delivery_date"],
		as_dict=True,
	)


@frappe.whitelist()
def get_container_status(container_number):
	container = frappe.db.get_value("Container", {"container_number": container_number}, "name")
	if not container:
		frappe.throw(_("Container not found"))
	if not frappe.has_permission("Container", "read", container):
		frappe.throw(_("Not permitted"), frappe.PermissionError)
	return frappe.db.get_value(
		"Container", container,
		["name", "container_status", "current_location", "job"],
		as_dict=True,
	)


@frappe.whitelist()
def get_shipment_status(job):
	# Shipment-level info lives directly on the Job in this app - there is
	# no separate Shipment doctype (see the Phase 1 architecture note).
	return get_job_status(job)


@frappe.whitelist()
def update_job_status(job, status):
	doc = frappe.get_doc("Clearing and Forwarding Job", job)
	if not doc.has_permission("write"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)
	doc.status = status
	doc.save()
	return {"name": doc.name, "status": doc.status}


@frappe.whitelist()
def create_job(**kwargs):
	if not frappe.has_permission("Clearing and Forwarding Job", "create"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)
	allowed_fields = {
		"job_type", "customer", "customer_reference", "branch", "company",
		"import_export", "mode_of_transport", "port_of_loading", "port_of_discharge",
		"estimated_revenue", "estimated_cost",
	}
	data = {k: v for k, v in kwargs.items() if k in allowed_fields}
	data["doctype"] = "Clearing and Forwarding Job"
	doc = frappe.get_doc(data)
	doc.insert()
	return {"name": doc.name}


@frappe.whitelist()
def create_delivery(job, delivery_date=None, remarks=None):
	"""Lightweight delivery confirmation endpoint - marks the Job Delivered
	and records the date. A full Proof of Delivery doctype (spec Section 37,
	with signature/photo/GPS capture) is out of scope for this drop."""
	doc = frappe.get_doc("Clearing and Forwarding Job", job)
	if not doc.has_permission("write"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)
	doc.delivery_date = delivery_date or frappe.utils.nowdate()
	doc.status = "Delivered"
	if remarks:
		doc.add_comment("Comment", remarks)
	doc.save()
	return {"name": doc.name, "status": doc.status}


@frappe.whitelist()
def generate_qr_code(doctype, docname):
	from clearing_forwarding.clearing_forwarding.utils.qr import generate_qr_code_file
	if not frappe.has_permission(doctype, "read", docname):
		frappe.throw(_("Not permitted"), frappe.PermissionError)
	return generate_qr_code_file(doctype, docname)
