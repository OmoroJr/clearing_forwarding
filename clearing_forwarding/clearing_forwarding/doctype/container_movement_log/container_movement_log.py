import frappe
from frappe.model.document import Document


class ContainerMovementLog(Document):
	def after_insert(self):
		self.sync_container()

	def sync_container(self):
		"""Keep Container.current_location / container_status in step with the
		latest movement entry, without requiring the user to update both."""
		if not self.container:
			return
		updates = {"current_location": self.new_location}
		if self.status:
			updates["container_status"] = self.status
		frappe.db.set_value("Container", self.container, updates)
