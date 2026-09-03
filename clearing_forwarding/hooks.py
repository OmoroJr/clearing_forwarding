from . import __version__ as app_version

app_name = "clearing_forwarding"
app_title = "Clearing Forwarding"
app_publisher = "Wycliffs"
app_description = "Clearing & Forwarding Management System for ERPNext 16"
app_email = ""
app_license = "Proprietary"
required_apps = ["erpnext"]

# Fixtures ------------------------------------------------------------------
fixtures = [
	{"dt": "Role", "filters": [["name", "in", [
		"C&F Manager",
		"Clearing Officer",
		"Forwarding Officer",
		"Documentation Officer",
		"Operations User",
	]]]},
	{"dt": "Custom Field", "filters": [["name", "in", [
		"Customer-cf_clearing_customer",
		"Customer-cf_shipping_customer",
		"Customer-cf_consignee",
		"Customer-cf_consignor",
		"Customer-cf_preferred_port",
		"Customer-cf_preferred_shipping_line",
		"Customer-cf_customs_code",
		"Customer-cf_importer_code",
		"Customer-cf_exporter_code",
		"Supplier-cf_transporter_type",
		"Supplier-cf_fleet_size",
		"Supplier-cf_rate_agreement",
		"Supplier-cf_compliance_status",
		"Supplier-cf_insurance_expiry",
		"Truck Trip-cf_job",
		"Purchase Invoice-cf_job",
		"Purchase Invoice-cf_container",
		"Purchase Invoice-cf_cost_type",
		"Sales Invoice-cf_job",
		"Sales Invoice-cf_container",
	]]]},
	{"dt": "Kanban Board", "filters": [["name", "=", "C&F Operations Board"]]},
]

# Document events -------------------------------------------------------------
# (Clearing & Forwarding Job handles validate/before_insert in its own
# controller - no doc_events needed for it.)
doc_events = {
	# ASSUMPTION (unconfirmed): Truck Trip's status field is named "status".
	# See utils/transport_integration.py for the single place to fix this
	# once transport_logistics' actual schema is confirmed.
	"Truck Trip": {
		"on_update": "clearing_forwarding.clearing_forwarding.utils.transport_integration.sync_job_from_truck_trip",
	},
	"Purchase Invoice": {
		"on_submit": "clearing_forwarding.clearing_forwarding.utils.job_finance.on_purchase_invoice_submit",
		"on_cancel": "clearing_forwarding.clearing_forwarding.utils.job_finance.on_purchase_invoice_cancel",
	},
	"Sales Invoice": {
		"on_submit": "clearing_forwarding.clearing_forwarding.utils.job_finance.on_sales_invoice_submit",
		"on_cancel": "clearing_forwarding.clearing_forwarding.utils.job_finance.on_sales_invoice_cancel",
	},
	"Payment Entry": {
		"on_submit": "clearing_forwarding.clearing_forwarding.utils.job_finance.on_payment_entry_change",
		"on_cancel": "clearing_forwarding.clearing_forwarding.utils.job_finance.on_payment_entry_change",
	},
}

# Scheduled tasks --------------------------------------------------------------
scheduler_events = {
	"daily": [
		"clearing_forwarding.clearing_forwarding.doctype.demurrage_and_detention.demurrage_and_detention.check_demurrage_alerts",
	],
}
