import frappe

# ---------------------------------------------------------------------------
# ASSUMPTIONS - unconfirmed against transport_logistics' real schema.
# Everything guessed about that app is isolated to this file: fix these
# three constants (and the JOB_STATUS_MAP if the status values differ)
# once you can check Truck Trip directly, and nothing elsewhere needs to
# change.
# ---------------------------------------------------------------------------
TRUCK_TRIP_DOCTYPE = "Truck Trip"
TRUCK_TRIP_JOB_FIELD = "cf_job"          # the Custom Field this app adds
TRUCK_TRIP_STATUS_FIELD = "status"        # guessed fieldname on Truck Trip

# Guessed Truck Trip status values -> Job status to advance to.
# Truck Trip's real status options are unconfirmed; adjust the left-hand
# side once known. Job status only ever advances, never regresses (same
# rule as the Customs Declaration sync in Phase 2).
JOB_STATUS_MAP = {
	"Planned": "Transport Scheduled",
	"Ongoing": "In Transit",
	"Completed": "Delivered",
}


def sync_job_from_truck_trip(doc, method=None):
	"""doc_events on_update handler for Truck Trip."""
	job_name = doc.get(TRUCK_TRIP_JOB_FIELD)
	if not job_name:
		return

	trip_status = doc.get(TRUCK_TRIP_STATUS_FIELD)
	target_status = JOB_STATUS_MAP.get(trip_status)
	if not target_status:
		return

	if not frappe.db.exists("Clearing and Forwarding Job", job_name):
		return

	job_status_options = (
		frappe.get_meta("Clearing and Forwarding Job").get_field("status").options.split("\n")
	)
	current_status = frappe.db.get_value("Clearing and Forwarding Job", job_name, "status")

	try:
		cur_idx = job_status_options.index(current_status)
		new_idx = job_status_options.index(target_status)
	except ValueError:
		return

	if new_idx > cur_idx:
		frappe.db.set_value("Clearing and Forwarding Job", job_name, "status", target_status)
