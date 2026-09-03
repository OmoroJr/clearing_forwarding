import frappe
from frappe import _
from frappe.utils import flt


def recalculate_job_financials(job_name):
	"""Recompute a Job's actual cost/revenue/profit/billing fields from its
	linked Job Cost Entry and Sales Invoice records. Writes directly via
	db_update (not save) to avoid re-triggering Job's own validate/hooks."""
	if not job_name or not frappe.db.exists("Clearing and Forwarding Job", job_name):
		return

	actual_cost = flt(frappe.db.sql(
		"select sum(amount) from `tabJob Cost Entry` where job=%s", job_name
	)[0][0])

	sales_invoices = frappe.get_all(
		"Sales Invoice",
		filters={"cf_job": job_name, "docstatus": 1},
		fields=["grand_total", "outstanding_amount"],
	)
	actual_revenue = sum(flt(si.grand_total) for si in sales_invoices)
	outstanding_amount = sum(flt(si.outstanding_amount) for si in sales_invoices)
	billed_amount = actual_revenue

	job = frappe.get_doc("Clearing and Forwarding Job", job_name)
	job.actual_cost = actual_cost
	job.actual_revenue = actual_revenue
	job.gross_profit = actual_revenue - actual_cost
	job.actual_margin_percent = (job.gross_profit / actual_revenue * 100) if actual_revenue else 0
	job.cost_variance = actual_cost - flt(job.estimated_cost)
	job.revenue_variance = actual_revenue - flt(job.estimated_revenue)
	job.billed_amount = billed_amount
	job.outstanding_amount = outstanding_amount

	if not billed_amount:
		job.payment_status = "Not Billed"
	elif outstanding_amount <= 0:
		job.payment_status = "Paid"
	elif outstanding_amount < billed_amount:
		job.payment_status = "Partially Paid"
	else:
		job.payment_status = "Billed"

	job.db_update()


# ---------------------------------------------------------------------------
# Purchase Invoice / Sales Invoice / Payment Entry doc_events
# ---------------------------------------------------------------------------

def on_purchase_invoice_submit(doc, method=None):
	if not doc.get("cf_job"):
		return
	entry = frappe.get_doc({
		"doctype": "Job Cost Entry",
		"job": doc.cf_job,
		"container": doc.get("cf_container"),
		"cost_type": doc.get("cf_cost_type") or "Miscellaneous",
		"supplier": doc.supplier,
		"purchase_invoice": doc.name,
		"amount": doc.grand_total,
		"currency": doc.currency,
		"posting_date": doc.posting_date,
	})
	entry.insert(ignore_permissions=True)
	recalculate_job_financials(doc.cf_job)


def on_purchase_invoice_cancel(doc, method=None):
	if not doc.get("cf_job"):
		return
	entries = frappe.get_all("Job Cost Entry", filters={"purchase_invoice": doc.name}, pluck="name")
	for name in entries:
		frappe.delete_doc("Job Cost Entry", name, ignore_permissions=True, force=True)
	recalculate_job_financials(doc.cf_job)


def on_sales_invoice_submit(doc, method=None):
	if doc.get("cf_job"):
		recalculate_job_financials(doc.cf_job)


def on_sales_invoice_cancel(doc, method=None):
	if doc.get("cf_job"):
		recalculate_job_financials(doc.cf_job)


def on_payment_entry_change(doc, method=None):
	jobs = set()
	for ref in doc.references:
		if ref.reference_doctype == "Sales Invoice":
			job = frappe.db.get_value("Sales Invoice", ref.reference_name, "cf_job")
			if job:
				jobs.add(job)
	for job in jobs:
		recalculate_job_financials(job)


# ---------------------------------------------------------------------------
# Customer credit control (spec Section 23) - off by default (CF Settings.
# enforce_credit_limit), and fails OPEN (logs + skips) rather than blocking
# Job submission if the credit-limit lookup itself hits an error, since this
# is a best-effort compliance check, not the accounting system of record.
# ---------------------------------------------------------------------------

def check_customer_credit(job):
	try:
		settings = frappe.get_single("CF Settings")
		if not settings.get("enforce_credit_limit"):
			return
		if not job.customer:
			return
		credit_limit = _get_customer_credit_limit(job.customer, job.company)
		if not credit_limit:
			return
		outstanding = flt(frappe.db.sql(
			"""select sum(outstanding_amount) from `tabSales Invoice`
			   where customer=%s and company=%s and docstatus=1""",
			(job.customer, job.company),
		)[0][0])
		projected = outstanding + flt(job.estimated_revenue)
		if projected > credit_limit:
			frappe.throw(_(
				"Job {0} would push {1}'s outstanding ({2}) plus this job's estimated "
				"revenue ({3}) above their credit limit ({4})"
			).format(job.name, job.customer, outstanding, job.estimated_revenue, credit_limit))
	except frappe.ValidationError:
		raise
	except Exception:
		frappe.log_error(frappe.get_traceback(), "CF credit limit check failed - skipped")


def _get_customer_credit_limit(customer, company):
	"""ERPNext stores credit limits per-company in a child table on Customer
	in modern versions; degrade to "no limit configured" rather than
	erroring if that shape does not match this site's ERPNext version."""
	try:
		rows = frappe.get_all(
			"Customer Credit Limit",
			filters={"parent": customer, "company": company},
			fields=["credit_limit"],
			parent_doctype="Customer",
		)
		if rows:
			return flt(rows[0].credit_limit)
	except Exception:
		pass
	return flt(frappe.db.get_value("Customer", customer, "credit_limit")) or None
