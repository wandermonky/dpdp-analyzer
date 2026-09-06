"""Severity-weighted gap scoring."""
from __future__ import annotations

from dataclasses import dataclass

from dpdp_analyzer.engine import Finding

WEIGHTS = {"critical": 8, "high": 4, "medium": 2, "low": 1}
SEVERITY_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1}


@dataclass
class CategoryBreakdown:
    category: str
    total: int
    failed: int
    score: float


@dataclass
class RemediationItem:
    rule_id: str
    category: str
    severity: str
    section_ref: str
    affected_rows: int


@dataclass
class ScoreResult:
    overall_score: float
    categories: list[CategoryBreakdown]
    remediation: list[RemediationItem]


def _weighted_score(findings: list[Finding]) -> float:
    possible = sum(WEIGHTS[f.severity] for f in findings)
    if possible == 0:
        return 100.0
    lost = sum(WEIGHTS[f.severity] for f in findings if not f.passed)
    return round(100 * (1 - lost / possible), 1)


def score(findings: list[Finding]) -> ScoreResult:
    overall = _weighted_score(findings)

    categories = []
    for cat in sorted({f.category for f in findings}):
        cat_findings = [f for f in findings if f.category == cat]
        categories.append(
            CategoryBreakdown(
                category=cat,
                total=len(cat_findings),
                failed=sum(1 for f in cat_findings if not f.passed),
                score=_weighted_score(cat_findings),
            )
        )

    failed_by_rule: dict[str, list[Finding]] = {}
    for f in findings:
        if not f.passed:
            failed_by_rule.setdefault(f.rule_id, []).append(f)

    remediation = [
        RemediationItem(
            rule_id=rule_id,
            category=fs[0].category,
            severity=fs[0].severity,
            section_ref=fs[0].section_ref,
            affected_rows=len({f.row_index for f in fs}),
        )
        for rule_id, fs in failed_by_rule.items()
    ]
    remediation.sort(key=lambda r: (SEVERITY_RANK[r.severity], r.affected_rows), reverse=True)

    return ScoreResult(overall_score=overall, categories=categories, remediation=remediation)
