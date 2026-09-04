import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import add_days, nowdate

from clearing_forwarding.clearing_forwarding.utils.job_finance import check_customer_credit


class ClearingandForwardingJob(Document):
	def autoname(self):
		prefix = get_branch_prefix(self.branch)
		series_key = f"{prefix}-CF-.YYYY.-.#####" if prefix else "CF-.YYYY.-.#####"
		self.name = make_autoname(series_key)

	def before_insert(self):
		if not self.status:
			self.status = "Draft"
		if not self.tasks:
			self._apply_task_templates()
		if not self.documents:
			self._apply_document_checklist_templates()

	def validate(self):
		self.calculate_profitability()

	def before_submit(self):
		check_customer_credit(self)

	def calculate_profitability(self):
		revenue = self.estimated_revenue or 0
		cost = self.estimated_cost or 0
		self.expected_profit = revenue - cost
		self.margin_percent = (self.expected_profit / revenue * 100) if revenue else 0

	def _apply_task_templates(self):
		settings = frappe.get_single("CF Settings")
		for row in settings.job_type_task_templates:
			if row.job_type and row.job_type != self.job_type:
				continue
			due_date = None
			if row.default_days_to_complete:
				due_date = add_days(nowdate(), row.default_days_to_complete)
			self.append("tasks", {
				"task_type": row.task_type,
				"priority": row.default_priority or "Medium",
				"due_date": due_date,
				"status": "Open",
			})

	def _apply_document_checklist_templates(self):
		settings = frappe.get_single("CF Settings")
		for row in settings.document_checklist_templates:
			if row.job_type and row.job_type != self.job_type:
				continue
			self.append("documents", {
				"document_type": row.document_type,
				"required": row.required,
			})


def get_branch_prefix(branch):
	if not branch:
		return None
	settings = frappe.get_single("CF Settings")
	for row in settings.branch_naming_map:
		if row.branch == branch:
			return row.prefix
	return None


# ---------------------------------------------------------------------------
# Cross-doctype status sync (used by Customs Declaration in Phase 2 onward)
# ---------------------------------------------------------------------------
JOB_STATUS_ORDER = [
	"Draft",
	"Quoted",
	"Job Open",
	"Documentation Pending",
	"Documents Complete",
	"Customs Processing",
	"Customs Assessment",
	"Duty Pending",
	"Duty Paid",
	"Customs Released",
	"Port Processing",
	"Cargo Released",
	"Transport Scheduled",
	"In Transit",
	"Delivered",
	"Billing Pending",
	"Billed",
	"Payment Pending",
	"Completed",
	"Cancelled",
]


def advance_job_status(job_name, new_status):
	"""Move a Job's status forward to new_status, never backward.
	Cancelled is left alone - a job can only be cancelled explicitly."""
	if not job_name or new_status not in JOB_STATUS_ORDER:
		return
	current = frappe.db.get_value("Clearing and Forwarding Job", job_name, "status")
	if not current or current not in JOB_STATUS_ORDER:
		return
	if current == "Cancelled":
		return
	if JOB_STATUS_ORDER.index(new_status) > JOB_STATUS_ORDER.index(current):
		frappe.db.set_value("Clearing and Forwarding Job", job_name, "status", new_status)
