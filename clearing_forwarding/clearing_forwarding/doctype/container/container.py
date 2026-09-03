import frappe
from frappe.model.document import Document


class Container(Document):
	def validate(self):
		self.calculate_cargo_weight()

	def calculate_cargo_weight(self):
		if self.gross_weight and self.tare_weight:
			self.cargo_weight = self.gross_weight - self.tare_weight
