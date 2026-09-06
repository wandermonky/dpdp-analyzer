"""Inventory row schema and file loader."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from pydantic import BaseModel, ValidationError


class InventoryRow(BaseModel):
    system_name: str
    data_category: str
    purpose: str
    consent_captured: bool
    retention_period_days: int
    cross_border_transfer: bool
    encryption_at_rest: bool
    is_child_or_disabled_data: bool
    parental_consent_captured: bool
    consent_log_maintained: bool
    consent_withdrawal_available: bool
    notice_provided: bool
    notice_itemized: bool
    notice_has_dpo_contact: bool
    notice_has_grievance_link: bool
    rights_access_enabled: bool
    rights_correction_erasure_enabled: bool
    grievance_mechanism_published: bool
    grievance_avg_resolution_days: int
    breach_notification_process_defined: bool
    breach_notify_individuals_without_delay: bool
    breach_report_72h_filed: bool
    is_significant_data_fiduciary: bool
    dpo_appointed_india_based: bool
    independent_auditor_appointed: bool
    dpia_conducted: bool
    sdf_reporting_to_board: bool


def load_inventory(path: str | Path) -> tuple[list[InventoryRow], list[str]]:
    """Read a CSV/XLSX inventory and validate every row.

    Never raises on bad data: a missing column produces one clear error, a
    bad value in a single row produces one error for that row (spreadsheet
    row number, 1-indexed with header as row 1) while every other row still
    loads.
    """
    path = Path(path)
    df = pd.read_excel(path) if path.suffix.lower() in (".xlsx", ".xls") else pd.read_csv(path)

    required = set(InventoryRow.model_fields)
    missing = required - set(df.columns)
    if missing:
        return [], [f"Missing required column(s): {', '.join(sorted(missing))}"]

    rows: list[InventoryRow] = []
    errors: list[str] = []
    for offset, record in enumerate(df.to_dict(orient="records")):
        row_number = offset + 2  # +1 for header, +1 for 1-indexing
        try:
            rows.append(InventoryRow(**record))
        except ValidationError as exc:
            details = "; ".join(f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors())
            errors.append(f"Row {row_number}: {details}")

    return rows, errors
