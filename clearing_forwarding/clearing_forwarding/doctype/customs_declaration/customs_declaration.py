import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt
from clearing_forwarding.clearing_forwarding.doctype.clearing_and_forwarding_job.clearing_and_forwarding_job import (
	advance_job_status,
)
from clearing_forwarding.clearing_forwarding.utils.notifications import notify_role

STATUS_ORDER = [
	"Draft",
	"Submitted",
	"Assessed",
	"Payment Pending",
	"Paid",
	"Customs Released",
	"Closed",
]

# Maps this doctype's status to the Job status it should push forward to.
JOB_STATUS_MAP = {
	"Submitted": "Customs Processing",
	"Assessed": "Customs Assessment",
	"Payment Pending": "Duty Pending",
	"Paid": "Duty Paid",
	"Customs Released": "Customs Released",
}

# Roles notified when status reaches a given point (Section 31 of the spec).
NOTIFY_ON_STATUS = {
	"Assessed": ("Accounts User", "Customs assessment ready for {0} (Job {1})"),
	"Payment Pending": ("Accounts User", "Duty payment pending for {0} (Job {1})"),
}

TAX_FIELDS = ["duty", "vat", "excise", "idf", "rdl", "other_taxes"]


class CustomsDeclaration(Document):
	def validate(self):
		self.calculate_total_taxes()
		self.validate_status_transition()

	def calculate_total_taxes(self):
		self.total_taxes = sum(flt(self.get(f)) for f in TAX_FIELDS)

	def validate_status_transition(self):
		if not self.get_doc_before_save():
			return
		old_status = self.get_doc_before_save().status
		if old_status == self.status:
			return
		if frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles():
			return
		try:
			old_idx = STATUS_ORDER.index(old_status)
			new_idx = STATUS_ORDER.index(self.status)
		except ValueError:
			return
		if new_idx != old_idx + 1:
			frappe.throw(_(
				"Status can only move forward one step at a time: {0} -> {1} is not allowed"
			).format(old_status, self.status))

	def on_submit(self):
		if self.status == "Draft":
			self.db_set("status", "Submitted")
		self.sync_job_status()

	def on_update(self):
		if self.docstatus == 1:
			self.sync_job_status()

	def sync_job_status(self):
		mapped = JOB_STATUS_MAP.get(self.status)
		if mapped:
			advance_job_status(self.job, mapped)
			frappe.db.set_value("Clearing and Forwarding Job", self.job, "customs_declaration", self.name)
			frappe.db.set_value("Clearing and Forwarding Job", self.job, "customs_status", self.status)
		self.send_status_notification()

	def send_status_notification(self):
		entry = NOTIFY_ON_STATUS.get(self.status)
		if not entry:
			return
		role, subject_template = entry
		notify_role(
			role,
			subject_template.format(self.name, self.job),
			reference_doctype=self.doctype,
			reference_name=self.name,
		)
