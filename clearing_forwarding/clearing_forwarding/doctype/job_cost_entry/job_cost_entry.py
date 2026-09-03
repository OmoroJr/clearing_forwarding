import frappe
from frappe.model.document import Document

from clearing_forwarding.clearing_forwarding.utils.job_finance import recalculate_job_financials


class JobCostEntry(Document):
	def after_insert(self):
		recalculate_job_financials(self.job)

	def on_update(self):
		recalculate_job_financials(self.job)

	def on_trash(self):
		recalculate_job_financials(self.job)
