import io

import frappe


def generate_qr_code_file(doctype, docname):
	"""Generates a QR code PNG (payload = this document's desk URL) and
	attaches it as a File on the document. Requires the `qrcode` package -
	see requirements.txt (`bench pip install qrcode[pil]` if it's missing
	on an existing bench)."""
	try:
		import qrcode
	except ImportError:
		frappe.throw(
			"The 'qrcode' Python package is required for QR generation. "
			"Run: bench pip install qrcode[pil]"
		)

	url = frappe.utils.get_url_to_form(doctype, docname)
	img = qrcode.make(url)
	buffer = io.BytesIO()
	img.save(buffer, format="PNG")
	buffer.seek(0)

	file_doc = frappe.get_doc({
		"doctype": "File",
		"file_name": f"{doctype}-{docname}-qr.png".replace(" ", "_"),
		"attached_to_doctype": doctype,
		"attached_to_name": docname,
		"content": buffer.getvalue(),
		"is_private": 0,
	})
	file_doc.save(ignore_permissions=True)
	return {"file_url": file_doc.file_url}
