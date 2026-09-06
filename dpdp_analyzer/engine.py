"""Rule-evaluation engine: runs every rule's check against every row."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from dpdp_analyzer.inventory import InventoryRow
from dpdp_analyzer.rules import Rule

CheckFn = Callable[[InventoryRow], tuple[bool, object]]

_EXEMPTED_CONSENT_PURPOSES = {"child_protection", "subsidy_delivery", "email_account_creation"}
_SENSITIVE_CATEGORIES = {"biometric_data", "health_data", "financial_data"}


def _consent_01(row: InventoryRow) -> tuple[bool, object]:
    passed = row.consent_captured or row.purpose in _EXEMPTED_CONSENT_PURPOSES
    return passed, row.consent_captured


def _consent_02(row: InventoryRow) -> tuple[bool, object]:
    passed = not row.is_child_or_disabled_data or row.parental_consent_captured
    return passed, row.parental_consent_captured


def _consent_03(row: InventoryRow) -> tuple[bool, object]:
    return row.consent_log_maintained, row.consent_log_maintained


def _consent_04(row: InventoryRow) -> tuple[bool, object]:
    return row.consent_withdrawal_available, row.consent_withdrawal_available


def _notice_01(row: InventoryRow) -> tuple[bool, object]:
    return row.notice_provided, row.notice_provided


def _notice_02(row: InventoryRow) -> tuple[bool, object]:
    return row.notice_itemized, row.notice_itemized


def _notice_03(row: InventoryRow) -> tuple[bool, object]:
    return row.notice_has_dpo_contact, row.notice_has_dpo_contact


def _notice_04(row: InventoryRow) -> tuple[bool, object]:
    return row.notice_has_grievance_link, row.notice_has_grievance_link


def _rights_01(row: InventoryRow) -> tuple[bool, object]:
    return row.rights_access_enabled, row.rights_access_enabled


def _rights_02(row: InventoryRow) -> tuple[bool, object]:
    return row.rights_correction_erasure_enabled, row.rights_correction_erasure_enabled


def _rights_03(row: InventoryRow) -> tuple[bool, object]:
    return row.grievance_mechanism_published, row.grievance_mechanism_published


def _rights_04(row: InventoryRow) -> tuple[bool, object]:
    return row.grievance_avg_resolution_days <= 90, row.grievance_avg_resolution_days


def _breach_01(row: InventoryRow) -> tuple[bool, object]:
    passed = row.data_category not in _SENSITIVE_CATEGORIES or row.encryption_at_rest
    return passed, row.encryption_at_rest


def _breach_02(row: InventoryRow) -> tuple[bool, object]:
    return row.breach_notification_process_defined, row.breach_notification_process_defined


def _breach_03(row: InventoryRow) -> tuple[bool, object]:
    return row.breach_notify_individuals_without_delay, row.breach_notify_individuals_without_delay


def _breach_04(row: InventoryRow) -> tuple[bool, object]:
    return row.breach_report_72h_filed, row.breach_report_72h_filed


def _sdf_01(row: InventoryRow) -> tuple[bool, object]:
    passed = not row.is_significant_data_fiduciary or row.dpo_appointed_india_based
    return passed, row.dpo_appointed_india_based


def _sdf_02(row: InventoryRow) -> tuple[bool, object]:
    passed = not row.is_significant_data_fiduciary or row.independent_auditor_appointed
    return passed, row.independent_auditor_appointed


def _sdf_03(row: InventoryRow) -> tuple[bool, object]:
    passed = not row.is_significant_data_fiduciary or row.dpia_conducted
    return passed, row.dpia_conducted


def _sdf_04(row: InventoryRow) -> tuple[bool, object]:
    passed = not row.is_significant_data_fiduciary or row.sdf_reporting_to_board
    return passed, row.sdf_reporting_to_board


CHECKS: dict[str, CheckFn] = {
    "consent-01": _consent_01,
    "consent-02": _consent_02,
    "consent-03": _consent_03,
    "consent-04": _consent_04,
    "notice-01": _notice_01,
    "notice-02": _notice_02,
    "notice-03": _notice_03,
    "notice-04": _notice_04,
    "rights-01": _rights_01,
    "rights-02": _rights_02,
    "rights-03": _rights_03,
    "rights-04": _rights_04,
    "breach-01": _breach_01,
    "breach-02": _breach_02,
    "breach-03": _breach_03,
    "breach-04": _breach_04,
    "sdf-01": _sdf_01,
    "sdf-02": _sdf_02,
    "sdf-03": _sdf_03,
    "sdf-04": _sdf_04,
}


@dataclass
class Finding:
    rule_id: str
    row_index: int
    passed: bool
    evidence: object
    severity: str
    section_ref: str
    category: str


def evaluate(rows: list[InventoryRow], rules: list[Rule]) -> list[Finding]:
    findings = []
    for row_index, row in enumerate(rows):
        for rule in rules:
            passed, evidence = CHECKS[rule.id](row)
            findings.append(
                Finding(
                    rule_id=rule.id,
                    row_index=row_index,
                    passed=passed,
                    evidence=evidence,
                    severity=rule.severity,
                    section_ref=rule.section_ref,
                    category=rule.category,
                )
            )
    return findings
