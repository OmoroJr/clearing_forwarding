# Clearing & Forwarding Management System

Custom Frappe app for ERPNext 16 covering Clearing & Forwarding (C&F)
operations: imports/exports, customs, freight forwarding, container
tracking, transport coordination, billing and job profitability.

All 7 phases of the original plan are in this drop.

## Install

```
bench get-app clearing_forwarding /path/to/clearing_forwarding
bench --site <site> install-app clearing_forwarding
bench --site <site> migrate
```

The `qrcode[pil]` Python package is a new dependency (Phase 7, QR code
generation) - it's in requirements.txt/setup.py so a normal
`bench get-app` install picks it up, but if you're upgrading an
existing bench install rather than installing fresh, run
`bench pip install qrcode[pil]` manually.

## What's in each phase

**Phase 1 - Foundation**: app skeleton, CF Settings, master data
(Shipping Line, Vessel, Port, Clearing Agent), Customer/Supplier
Custom Fields, the core **Clearing and Forwarding Job** doctype
(branch-aware naming, auto task/document-checklist creation from
templates), roles, workspace.

**Phase 2 - Customs**: **Government Agency** master (generic across
Customs and any other regulator), **Customs Declaration** (submittable,
forward-only status workflow, auto tax rollup), **Job Agency
Clearance** child table for parallel multi-agency sign-off, Issuing
Agency on Job Document, automatic Job status sync from Customs
Declaration, in-app notifications via Notification Log.

**Phase 3 - Container**: **Container** (auto cargo weight),
**Container Movement Log** (standalone, high-volume), **Demurrage And
Detention** (auto free-time/overdue/charge calc, daily 5/3/1-day and
expiry alerts).

**Phase 4 - Transport**: **Shipment Incident**, and a
`transport_logistics` integration (Truck Trip `cf_job` link + Job-side
status rollup) built on assumed field names - see
`utils/transport_integration.py` for the constants to correct once you
can confirm Truck Trip's real schema.

**Phase 5 - Finance**: **Job Cost Entry** (cost ledger), **Job Cost
Allocation** (split one shared supplier invoice across jobs by
Equal/Weight/Volume/Container/Manual share), Purchase Invoice / Sales
Invoice / Payment Entry linked back to the Job, automatic actual
cost/revenue/profit/variance/billing-status recalculation, opt-in
customer credit-limit check on Job submit (fails open on lookup
errors).

**Phase 6 - Dashboards & Reporting**: 8 Script Reports (Job Register,
Job Profitability, Customer Profitability, Job Costing, Demurrage,
Document Compliance, Outstanding Customer, Unbilled Jobs) with filter
UIs and native Excel/CSV export; a Kanban Board on Job.status (all 20
states as columns); 5 Number Cards for an executive-dashboard view
(not auto-wired into the Workspace's chart blocks - drag them on via
the UI, a 30-second step).

**Phase 7 - Portal & Integrations**:
- **CF Integration Settings** (single doctype) - credential storage
  for SMS, WhatsApp, M-Pesa Daraja, GPS, and customs/port APIs, using
  Frappe's Password fieldtype (encrypted at rest). Storage only - no
  provider-specific send/receive logic is wired up in this drop.
- **QR codes** - `utils/qr.py` generates a QR (payload: the document's
  desk URL) and attaches it as a File; callable via the
  `generate_qr_code` API method or from a print format.
- **REST API** (`clearing_forwarding/api.py`) - `get_job_status`,
  `get_container_status`, `get_shipment_status` (aliases Job, since
  there's no separate Shipment doctype), `update_job_status`,
  `create_job`, `create_delivery` (a lightweight status-only
  confirmation - no signature/photo/GPS capture; a full Proof of
  Delivery doctype per spec Section 37 is out of scope here), and
  `generate_qr_code`. All permission-checked via `frappe.has_permission`.
- **Customer portal**:
  - `/track` - public, no login. Accepts a Job Number, Container
    Number, or BL Number and shows a coarse 6-stage progress bar
    (Job Created -> Documents -> Customs -> Port -> Transport ->
    Delivery) with no financial data, per spec Section 34.
  - `/my-jobs` - logged-in customer portal. Lists jobs for whichever
    Customer(s) the logged-in user has a User Permission for (the
    standard ERPNext way of tying a portal login to a Customer) -
    status, ETA, billed/outstanding amounts.

## Known gaps / deliberate simplifications

- Truck Trip integration field names are guessed (Phase 4) - confirm
  and fix `utils/transport_integration.py`'s constants when you can.
- Number Cards ship standalone rather than wired into the Workspace's
  chart/card blocks (Phase 6) - that child-table schema wasn't safe to
  guess without a live site.
- No Container-level or Shipment-level doctype for "Delivery
  Trip" beyond the `transport_logistics` Truck Trip link - the spec's
  fleet/driver/vehicle doctypes are intentionally not duplicated here.
- Proof of Delivery is a status flag, not a full signature/photo/GPS
  capture doctype.
- Integration Settings stores credentials only; no SMS/WhatsApp/M-Pesa
  send logic is implemented against them yet.
