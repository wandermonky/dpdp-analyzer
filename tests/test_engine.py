from pathlib import Path

import pytest

from dpdp_analyzer.engine import CHECKS, evaluate
from dpdp_analyzer.inventory import InventoryRow, load_inventory
from dpdp_analyzer.rules import load_rules

RULES_PATH = Path(__file__).parent.parent / "rules" / "dpdp_v1.yaml"
SAMPLE = Path(__file__).parent.parent / "dpdp_analyzer" / "sample_inventory.csv"

BASELINE = dict(
    system_name="TestSystem",
    data_category="contact_info",
    purpose="customer_support",
    consent_captured=True,
    retention_period_days=365,
    cross_border_transfer=False,
    encryption_at_rest=True,
    is_child_or_disabled_data=False,
    parental_consent_captured=False,
    consent_log_maintained=True,
    consent_withdrawal_available=True,
    notice_provided=True,
    notice_itemized=True,
    notice_has_dpo_contact=True,
    notice_has_grievance_link=True,
    rights_access_enabled=True,
    rights_correction_erasure_enabled=True,
    grievance_mechanism_published=True,
    grievance_avg_resolution_days=30,
    breach_notification_process_defined=True,
    breach_notify_individuals_without_delay=True,
    breach_report_72h_filed=True,
    is_significant_data_fiduciary=False,
    dpo_appointed_india_based=False,
    independent_auditor_appointed=False,
    dpia_conducted=False,
    sdf_reporting_to_board=False,
)


def make_row(**overrides) -> InventoryRow:
    return InventoryRow(**{**BASELINE, **overrides})


# rule_id -> (overrides that should PASS, overrides that should FAIL)
CASES = {
    "consent-01": ({}, {"consent_captured": False}),
    "consent-02": (
        {"is_child_or_disabled_data": True, "parental_consent_captured": True},
        {"is_child_or_disabled_data": True, "parental_consent_captured": False},
    ),
    "consent-03": ({}, {"consent_log_maintained": False}),
    "consent-04": ({}, {"consent_withdrawal_available": False}),
    "notice-01": ({}, {"notice_provided": False}),
    "notice-02": ({}, {"notice_itemized": False}),
    "notice-03": ({}, {"notice_has_dpo_contact": False}),
    "notice-04": ({}, {"notice_has_grievance_link": False}),
    "rights-01": ({}, {"rights_access_enabled": False}),
    "rights-02": ({}, {"rights_correction_erasure_enabled": False}),
    "rights-03": ({}, {"grievance_mechanism_published": False}),
    "rights-04": ({}, {"grievance_avg_resolution_days": 91}),
    "breach-01": (
        {"data_category": "biometric_data", "encryption_at_rest": True},
        {"data_category": "biometric_data", "encryption_at_rest": False},
    ),
    "breach-02": ({}, {"breach_notification_process_defined": False}),
    "breach-03": ({}, {"breach_notify_individuals_without_delay": False}),
    "breach-04": ({}, {"breach_report_72h_filed": False}),
    "sdf-01": (
        {"is_significant_data_fiduciary": True, "dpo_appointed_india_based": True},
        {"is_significant_data_fiduciary": True, "dpo_appointed_india_based": False},
    ),
    "sdf-02": (
        {"is_significant_data_fiduciary": True, "independent_auditor_appointed": True},
        {"is_significant_data_fiduciary": True, "independent_auditor_appointed": False},
    ),
    "sdf-03": (
        {"is_significant_data_fiduciary": True, "dpia_conducted": True},
        {"is_significant_data_fiduciary": True, "dpia_conducted": False},
    ),
    "sdf-04": (
        {"is_significant_data_fiduciary": True, "sdf_reporting_to_board": True},
        {"is_significant_data_fiduciary": True, "sdf_reporting_to_board": False},
    ),
}


def test_every_rule_id_has_a_check_case():
    rules = load_rules(RULES_PATH)
    assert {r.id for r in rules} == set(CASES)
    assert set(CHECKS) == set(CASES)


@pytest.mark.parametrize("rule_id", CASES)
def test_rule_passes_on_compliant_row(rule_id):
    pass_overrides, _ = CASES[rule_id]
    passed, _ = CHECKS[rule_id](make_row(**pass_overrides))
    assert passed is True


@pytest.mark.parametrize("rule_id", CASES)
def test_rule_fails_on_noncompliant_row(rule_id):
    _, fail_overrides = CASES[rule_id]
    passed, _ = CHECKS[rule_id](make_row(**fail_overrides))
    assert passed is False


def test_evaluate_produces_a_finding_per_row_per_rule():
    rows, errors = load_inventory(SAMPLE)
    rules = load_rules(RULES_PATH)
    assert errors == []

    findings = evaluate(rows, rules)

    assert len(findings) == len(rows) * len(rules)
    assert {f.rule_id for f in findings} == {r.id for r in rules}
    assert any(f.passed for f in findings)
    assert any(not f.passed for f in findings)
