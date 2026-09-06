from pathlib import Path

from dpdp_analyzer.engine import evaluate
from dpdp_analyzer.inventory import load_inventory
from dpdp_analyzer.report import (
    DISCLAIMER,
    render_html,
    render_report,
    render_report_json,
)
from dpdp_analyzer.rules import load_rules
from dpdp_analyzer.scoring import score

RULES_PATH = Path(__file__).parent.parent / "rules" / "dpdp_v1.yaml"
SAMPLE = Path(__file__).parent.parent / "dpdp_analyzer" / "sample_inventory.csv"


def _sample_score_and_rules():
    rows, errors = load_inventory(SAMPLE)
    assert errors == []
    rules = load_rules(RULES_PATH)
    findings = evaluate(rows, rules)
    return score(findings), rules


def test_render_html_always_includes_disclaimer():
    score_result, rules = _sample_score_and_rules()
    html = render_html(score_result, rules)
    assert DISCLAIMER in html


def test_render_report_json_matches_html_data():
    score_result, rules = _sample_score_and_rules()
    data = render_report_json(score_result, rules)
    assert data["overall_score"] == score_result.overall_score
    assert data["disclaimer"] == DISCLAIMER
    assert len(data["remediation"]) == len(score_result.remediation)
    assert len(data["categories"]) == len(score_result.categories)


def test_render_report_produces_an_openable_pdf(tmp_path):
    score_result, rules = _sample_score_and_rules()
    out_path = tmp_path / "report.pdf"

    render_report(score_result, rules, out_path)

    assert out_path.exists()
    content = out_path.read_bytes()
    assert content.startswith(b"%PDF-")
    assert len(content) > 1000
