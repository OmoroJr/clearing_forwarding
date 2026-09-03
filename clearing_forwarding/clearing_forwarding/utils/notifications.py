import frappe


def notify_role(role, subject, reference_doctype, reference_name, notification_type="Alert"):
	"""Create an in-app Notification Log entry for every enabled user holding `role`.

	Deliberately uses the core "Notification Log" doctype (the bell-icon feed)
	directly, rather than fixturing the core "Notification" trigger doctype -
	that doctype's schema has shifted across Frappe versions and getting it
	wrong silently breaks migrate. Notification Log's core fields
	(for_user, from_user, type, subject, document_type, document_name) have
	been stable, so this is the safer integration point.
	"""
	user_names = frappe.get_all(
		"Has Role",
		filters={"role": role, "parenttype": "User"},
		pluck="parent",
	)
	if not user_names:
		return

	enabled_users = frappe.get_all(
		"User",
		filters={"name": ["in", user_names], "enabled": 1},
		pluck="name",
	)

	for user in enabled_users:
		if user == frappe.session.user:
			continue
		frappe.get_doc({
			"doctype": "Notification Log",
			"subject": subject,
			"for_user": user,
			"from_user": frappe.session.user,
			"type": notification_type,
			"document_type": reference_doctype,
			"document_name": reference_name,
		}).insert(ignore_permissions=True)
