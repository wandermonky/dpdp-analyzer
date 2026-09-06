from dpdp_analyzer.engine import Finding
from dpdp_analyzer.scoring import score


def make_finding(rule_id, passed, severity, category="consent", row_index=0, section_ref="S. 1"):
    return Finding(
        rule_id=rule_id,
        row_index=row_index,
        passed=passed,
        evidence=None,
        severity=severity,
        section_ref=section_ref,
        category=category,
    )


def test_all_pass_scores_100():
    findings = [
        make_finding("r1", True, "critical"),
        make_finding("r2", True, "high"),
        make_finding("r3", True, "medium"),
        make_finding("r4", True, "low"),
    ]
    result = score(findings)
    assert result.overall_score == 100.0
    assert result.remediation == []


def test_all_fail_scores_zero():
    findings = [
        make_finding("r1", False, "critical"),
        make_finding("r2", False, "high"),
        make_finding("r3", False, "medium"),
        make_finding("r4", False, "low"),
    ]
    result = score(findings)
    assert result.overall_score == 0.0


def test_mixed_case_matches_hand_calculated_score():
    # points_possible = 8 (critical) + 4 (high) + 2 (medium) + 1 (low) = 15
    # points_lost = 8 (critical failed) + 2 (medium failed) = 10
    # overall = 100 * (1 - 10/15) = 33.333... -> 33.3
    findings = [
        make_finding("r1", False, "critical"),
        make_finding("r2", True, "high"),
        make_finding("r3", False, "medium"),
        make_finding("r4", True, "low"),
    ]
    result = score(findings)
    assert result.overall_score == 33.3


def test_category_breakdown_shows_where_weakest():
    findings = [
        make_finding("c1", False, "critical", category="consent"),
        make_finding("n1", True, "critical", category="notice"),
    ]
    result = score(findings)
    by_category = {c.category: c for c in result.categories}
    assert by_category["consent"].score == 0.0
    assert by_category["notice"].score == 100.0


def test_remediation_sorted_by_severity_then_affected_rows():
    findings = [
        make_finding("medium-wide", False, "medium", row_index=0),
        make_finding("medium-wide", False, "medium", row_index=1),
        make_finding("medium-wide", False, "medium", row_index=2),
        make_finding("critical-narrow", False, "critical", row_index=0),
        make_finding("critical-wide", False, "critical", row_index=0),
        make_finding("critical-wide", False, "critical", row_index=1),
    ]
    result = score(findings)
    order = [r.rule_id for r in result.remediation]
    assert order == ["critical-wide", "critical-narrow", "medium-wide"]
