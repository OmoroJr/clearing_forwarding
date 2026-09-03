import frappe

# Deliberately a short, coarse list - never the same granular status shown
# internally, and never any financial fields (spec Section 34: "without
# exposing confidential financial data").
PROGRESS_STAGES = [
	("Job Created", ["Draft", "Quoted", "Job Open"]),
	("Documents", ["Documentation Pending", "Documents Complete"]),
	("Customs", ["Customs Processing", "Customs Assessment", "Duty Pending", "Duty Paid", "Customs Released"]),
	("Port", ["Port Processing", "Cargo Released"]),
	("Transport", ["Transport Scheduled", "In Transit"]),
	("Delivery", ["Delivered", "Billing Pending", "Billed", "Payment Pending", "Completed"]),
]

no_cache = 1


def get_context(context):
	context.no_cache = 1
	query = frappe.form_dict.get("q") or frappe.form_dict.get("job") or ""
	query = query.strip()
	context.query = query
	context.result = None
	context.stages = [s[0] for s in PROGRESS_STAGES]
	context.current_stage_index = -1

	if not query:
		return context

	job_name = _find_job(query)
	if not job_name:
		context.not_found = True
		return context

	job = frappe.db.get_value(
		"Clearing and Forwarding Job", job_name,
		["name", "status", "eta", "etd", "delivery_date", "port_of_loading", "port_of_discharge"],
		as_dict=True,
	)
	context.result = job
	context.current_stage_index = _stage_index(job.status)
	return context


def _find_job(query):
	# Accept a Job Number, Container Number, or BL Number.
	if frappe.db.exists("Clearing and Forwarding Job", query):
		return query
	job = frappe.db.get_value("Clearing and Forwarding Job", {"bill_of_lading_number": query}, "name")
	if job:
		return job
	container_job = frappe.db.get_value("Container", {"container_number": query}, "job")
	if container_job:
		return container_job
	return None


def _stage_index(status):
	for i, (label, statuses) in enumerate(PROGRESS_STAGES):
		if status in statuses:
			return i
	return -1
