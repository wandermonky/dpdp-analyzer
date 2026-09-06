"""Minimal Streamlit UI: upload a CSV, see the score, download the PDF.

Wraps the same pipeline as the CLI (dpdp_analyzer/cli.py) -- no separate logic.
"""
from pathlib import Path
from tempfile import NamedTemporaryFile

import streamlit as st

from dpdp_analyzer.engine import evaluate
from dpdp_analyzer.inventory import load_inventory
from dpdp_analyzer.report import render_report
from dpdp_analyzer.rules import load_rules
from dpdp_analyzer.scoring import score

RULES_PATH = Path(__file__).parent / "rules" / "dpdp_v1.yaml"

st.title("DPDP Gap Analyzer")
st.caption("Not legal advice. Verify findings against the current DPDP Act and Rules before acting on them.")

uploaded = st.file_uploader("Upload a data-processing inventory (CSV)", type="csv")

if uploaded:
    with NamedTemporaryFile(suffix=".csv", delete=False) as tmp_csv:
        tmp_csv.write(uploaded.getvalue())
        csv_path = Path(tmp_csv.name)

    rules = load_rules(RULES_PATH)
    rows, errors = load_inventory(csv_path)

    if errors:
        st.warning("Some rows had issues:\n" + "\n".join(f"- {e}" for e in errors))

    if rows:
        findings = evaluate(rows, rules)
        result = score(findings)

        st.metric("Readiness score", f"{result.overall_score} / 100")

        st.subheader("Category breakdown")
        st.table([{"category": c.category, "findings": c.total, "failed": c.failed, "score": c.score} for c in result.categories])

        st.subheader("Remediation checklist")
        st.table(
            [
                {"severity": r.severity, "rule": r.rule_id, "category": r.category, "section": r.section_ref, "rows affected": r.affected_rows}
                for r in result.remediation
            ]
        )

        with NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
            render_report(result, rules, tmp_pdf.name)
            pdf_bytes = Path(tmp_pdf.name).read_bytes()

        st.download_button("Download PDF report", data=pdf_bytes, file_name="dpdp_report.pdf", mime="application/pdf")
    else:
        st.error("No valid rows in this file.")
