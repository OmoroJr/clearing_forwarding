import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate

from clearing_forwarding.clearing_forwarding.utils.job_finance import recalculate_job_financials

BASIS_FIELD_BY_METHOD = {
	"Weight-Based": "gross_weight",
	"Volume-Based": "cbm",
	"Container-Based": "container_count",
}


class JobCostAllocation(Document):
	def validate(self):
		self.calculate_allocations()

	def calculate_allocations(self):
		if not self.allocations:
			return
		total = flt(self.total_amount)
		method = self.allocation_method

		if method == "Equal":
			share = total / len(self.allocations)
			for row in self.allocations:
				row.allocated_amount = share

		elif method in BASIS_FIELD_BY_METHOD:
			basis_field = BASIS_FIELD_BY_METHOD[method]
			total_basis = 0.0
			for row in self.allocations:
				row.share_basis = flt(
					frappe.db.get_value("Clearing and Forwarding Job", row.job, basis_field)
				)
				total_basis += row.share_basis
			if not total_basis:
				frappe.throw(_(
					"None of the selected Jobs have a {0} value to allocate by - use Manual instead"
				).format(basis_field))
			for row in self.allocations:
				row.allocated_amount = total * (row.share_basis / total_basis)

		elif method == "Manual":
			manual_total = sum(flt(row.share_basis) for row in self.allocations)
			if round(manual_total, 2) != round(total, 2):
				frappe.throw(_(
					"Manual allocation shares ({0}) must add up to the Total Amount ({1})"
				).format(manual_total, total))
			for row in self.allocations:
				row.allocated_amount = flt(row.share_basis)

	def on_submit(self):
		affected_jobs = set()
		for row in self.allocations:
			entry = frappe.get_doc({
				"doctype": "Job Cost Entry",
				"job": row.job,
				"cost_type": self.cost_type,
				"purchase_invoice": self.source_purchase_invoice,
				"job_cost_allocation": self.name,
				"amount": row.allocated_amount,
				"posting_date": nowdate(),
			})
			entry.insert(ignore_permissions=True)
			affected_jobs.add(row.job)
		for job in affected_jobs:
			recalculate_job_financials(job)

	def on_cancel(self):
		affected_jobs = set()
		entries = frappe.get_all(
			"Job Cost Entry", filters={"job_cost_allocation": self.name}, pluck="name"
		)
		for name in entries:
			doc = frappe.get_doc("Job Cost Entry", name)
			affected_jobs.add(doc.job)
			doc.delete(ignore_permissions=True)
		for job in affected_jobs:
			recalculate_job_financials(job)
