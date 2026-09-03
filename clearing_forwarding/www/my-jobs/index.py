import frappe

no_cache = 1


def get_context(context):
	context.no_cache = 1
	if frappe.session.user == "Guest":
		frappe.throw("Please log in to view your jobs", frappe.PermissionError)

	customers = frappe.get_all(
		"User Permission",
		filters={"user": frappe.session.user, "allow": "Customer"},
		pluck="for_value",
	)

	if not customers:
		context.jobs = []
		context.no_customer_linked = True
		return context

	context.jobs = frappe.get_all(
		"Clearing and Forwarding Job",
		filters={"customer": ["in", customers]},
		fields=["name", "job_type", "status", "eta", "delivery_date", "billed_amount", "outstanding_amount"],
		order_by="creation desc",
		limit_page_length=100,
	)
	return context
