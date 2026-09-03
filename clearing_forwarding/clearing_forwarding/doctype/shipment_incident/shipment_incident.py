import frappe
from frappe.model.document import Document

from clearing_forwarding.clearing_forwarding.utils.notifications import notify_role


class ShipmentIncident(Document):
	def after_insert(self):
		if self.severity in ("High", "Critical"):
			notify_role(
				"C&F Manager",
				f"{self.severity} severity incident on Job {self.job}: {self.incident_type}",
				reference_doctype=self.doctype,
				reference_name=self.name,
			)
