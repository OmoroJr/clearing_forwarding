import frappe
from frappe.model.document import Document
from frappe.utils import add_days, getdate, nowdate

from clearing_forwarding.clearing_forwarding.utils.notifications import notify_role


class DemurrageAndDetention(Document):
	def validate(self):
		self.calculate_free_time_end()
		self.calculate_days_overdue()
		self.calculate_total_charge()
		self.update_status()
		self.sync_container()

	def calculate_free_time_end(self):
		if self.free_time_start and self.free_days is not None:
			self.free_time_end = add_days(self.free_time_start, self.free_days)

	def calculate_days_overdue(self):
		if not self.free_time_end:
			self.days_overdue = 0
			return
		end_point = getdate(self.actual_return_date) if self.actual_return_date else getdate(nowdate())
		delta = (end_point - getdate(self.free_time_end)).days
		self.days_overdue = delta if delta > 0 else 0

	def calculate_total_charge(self):
		self.total_charge = (self.days_overdue or 0) * (self.daily_rate or 0)

	def update_status(self):
		if self.actual_return_date and self.days_overdue == 0:
			self.status = "Cleared"
			return
		if not self.free_time_end:
			return
		days_remaining = (getdate(self.free_time_end) - getdate(nowdate())).days
		if days_remaining < 0:
			self.status = "Overdue"
		elif days_remaining <= 5:
			self.status = "Nearing Expiry"
		else:
			self.status = "Within Free Time"

	def sync_container(self):
		if not self.container:
			return
		frappe.db.set_value("Container", self.container, {
			"demurrage_record": self.name,
			"demurrage_status": self.status,
		})


def check_demurrage_alerts():
	"""Scheduled daily: fire the 5/3/1-day-remaining and Expired alerts
	from spec Section 9. Natural day-by-day granularity means each
	threshold is hit once as days_remaining counts down - no separate
	de-duplication bookkeeping needed."""
	rows = frappe.get_all(
		"Demurrage And Detention",
		filters={"status": ["!=", "Cleared"]},
		fields=["name", "container", "job", "free_time_end", "status"],
	)
	for row in rows:
		if not row.free_time_end:
			continue
		days_remaining = (getdate(row.free_time_end) - getdate(nowdate())).days
		if days_remaining in (5, 3, 1):
			_notify(row, f"{days_remaining} day(s) remaining before demurrage free time expires")
		elif days_remaining < 0 and row.status != "Overdue":
			_notify(row, "Demurrage free time has expired")


def _notify(row, message):
	subject = f"{message} - Container {row.container} (Job {row.job})"
	notify_role("CF Manager", subject, reference_doctype="Demurrage And Detention", reference_name=row.name)
