# Inventory field guide

This is the data dictionary for the data-processing inventory file you feed
into `dpdp-check` (CSV or XLSX, one row per system/data flow). Every column
below is required — a missing column fails validation with a clear error
before any rule runs.

Use [`dpdp_analyzer/inventory_template.csv`](../dpdp_analyzer/inventory_template.csv)
as your starting point: copy it, rename it, and replace the one example row
with a row per system in your organization. The bundled
[`sample_inventory.csv`](../dpdp_analyzer/sample_inventory.csv) has 12 fully
filled-in synthetic rows if you want to see more examples.

| # | Column | Type | Example | What it means | DPDP rule(s) it feeds |
|---|---|---|---|---|---|
| 1 | `system_name` | text | `CustomerCRM` | Name of the system or data flow being audited | (identifier only) |
| 2 | `data_category` | text | `biometric_data` | Category of personal data processed | `breach-01` |
| 3 | `purpose` | text | `customer_support` | Why the data is processed | `consent-01` |
| 4 | `consent_captured` | true/false | `true` | Verifiable consent obtained before processing | `consent-01` |
| 5 | `retention_period_days` | number | `365` | How long the data is kept, in days | (informational — see Limitations) |
| 6 | `cross_border_transfer` | true/false | `false` | Whether the data leaves India | (informational — see Limitations) |
| 7 | `encryption_at_rest` | true/false | `true` | Whether the data is encrypted at rest | `breach-01` |
| 8 | `is_child_or_disabled_data` | true/false | `false` | Data belongs to a child or person with a disability | `consent-02` |
| 9 | `parental_consent_captured` | true/false | `false` | Verifiable parental/guardian consent obtained | `consent-02` |
| 10 | `consent_log_maintained` | true/false | `true` | A retrievable consent record is kept, not just a yes/no flag | `consent-03` |
| 11 | `consent_withdrawal_available` | true/false | `true` | Users can withdraw consent as easily as they gave it | `consent-04` |
| 12 | `notice_provided` | true/false | `true` | A standalone notice is given before/at consent | `notice-01` |
| 13 | `notice_itemized` | true/false | `true` | The notice itemizes what data is collected and why | `notice-02` |
| 14 | `notice_has_dpo_contact` | true/false | `true` | The notice includes DPO/contact-person details | `notice-03` |
| 15 | `notice_has_grievance_link` | true/false | `true` | The notice links directly to consent withdrawal and complaints | `notice-04` |
| 16 | `rights_access_enabled` | true/false | `true` | Data principals can access their data | `rights-01` |
| 17 | `rights_correction_erasure_enabled` | true/false | `true` | Data principals can request correction/erasure | `rights-02` |
| 18 | `grievance_mechanism_published` | true/false | `true` | A public grievance redressal mechanism exists (website/app) | `rights-03` |
| 19 | `grievance_avg_resolution_days` | number | `30` | Average days to resolve a grievance | `rights-04` (must be ≤ 90) |
| 20 | `breach_notification_process_defined` | true/false | `true` | A breach notification runbook/process exists | `breach-02` |
| 21 | `breach_notify_individuals_without_delay` | true/false | `true` | Affected individuals are notified without delay on breach | `breach-03` |
| 22 | `breach_report_72h_filed` | true/false | `true` | Detailed breach reports are filed within 72 hours | `breach-04` |
| 23 | `is_significant_data_fiduciary` | true/false | `false` | This system/org is classified as a Significant Data Fiduciary (SDF) | gates rules 24-27 |
| 24 | `dpo_appointed_india_based` | true/false | `false` | An India-based DPO is appointed | `sdf-01` (only checked if #23 is true) |
| 25 | `independent_auditor_appointed` | true/false | `false` | An independent data auditor is appointed | `sdf-02` (only checked if #23 is true) |
| 26 | `dpia_conducted` | true/false | `false` | Periodic Data Protection Impact Assessments are conducted | `sdf-03` (only checked if #23 is true) |
| 27 | `sdf_reporting_to_board` | true/false | `false` | Significant findings are regularly reported to the Data Protection Board | `sdf-04` (only checked if #23 is true) |

**Notes:**
- Columns 24-27 only matter when `is_significant_data_fiduciary` is `true` —
  the rules pass vacuously for non-SDF rows, so it's fine to leave them
  `false` if the row isn't an SDF.
- `true`/`false` values are case-insensitive and also accept `1`/`0` or
  `yes`/`no` — Pydantic coerces them.
- To see exactly which rule checks which field and how, look at
  `dpdp_analyzer/engine.py` (one small function per rule) or
  `rules/dpdp_v1.yaml` (the `check` field on each rule entry).
