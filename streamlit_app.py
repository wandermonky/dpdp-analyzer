"""Interactive Streamlit UI: upload a CSV, see the score, download the PDF.

Wraps the same pipeline as the CLI (dpdp_analyzer/cli.py) -- no separate logic.
"""
from pathlib import Path
from tempfile import NamedTemporaryFile

import pandas as pd
import streamlit as st

from dpdp_analyzer.engine import evaluate
from dpdp_analyzer.inventory import load_inventory
from dpdp_analyzer.report import DISCLAIMER, render_report, render_report_json
from dpdp_analyzer.rules import load_rules
from dpdp_analyzer.scoring import score

RULES_PATH = Path(__file__).parent / "rules" / "dpdp_v1.yaml"
SAMPLE_PATH = Path(__file__).parent / "dpdp_analyzer" / "sample_inventory.csv"

SEVERITY_COLORS = {
    "critical": "#b30000",
    "high": "#e07b00",
    "medium": "#cca300",
    "low": "#6b6b6b",
}

st.set_page_config(page_title="DPDP Gap Analyzer", layout="wide")

st.title("DPDP Gap Analyzer")
st.caption(DISCLAIMER)

with st.sidebar:
    st.header("About")
    st.write(
        "Scores a data-processing inventory against 20 DPDP rules across "
        "consent, notice, data-principal rights, breach notification, and "
        "Significant Data Fiduciary obligations."
    )
    st.write(f"Rule pack: `{RULES_PATH.name}` — every rule is `status: draft`.")
    st.divider()
    with open(SAMPLE_PATH, "rb") as f:
        st.download_button("Download sample inventory", data=f.read(), file_name="sample_inventory.csv", mime="text/csv")

uploaded = st.file_uploader("Upload a data-processing inventory (CSV)", type="csv")

if not uploaded:
    st.info("Upload a CSV to get started, or grab the sample from the sidebar.")
    st.stop()

with NamedTemporaryFile(suffix=".csv", delete=False) as tmp_csv:
    tmp_csv.write(uploaded.getvalue())
    csv_path = Path(tmp_csv.name)

with st.spinner("Validating and scoring..."):
    rules = load_rules(RULES_PATH)
    rows, errors = load_inventory(csv_path)

if errors:
    with st.expander(f"{len(errors)} row(s) had validation issues", expanded=False):
        for error in errors:
            st.write(f"- {error}")

if not rows:
    st.error("No valid rows in this file. Fix the issues above and re-upload.")
    st.stop()

findings = evaluate(rows, rules)
result = score(findings)
report_data = render_report_json(result, rules)

col1, col2 = st.columns([1, 2])
with col1:
    st.metric("Readiness score", f"{result.overall_score} / 100")
    st.progress(min(result.overall_score, 100) / 100)
with col2:
    failed_count = sum(1 for f in findings if not f.passed)
    st.markdown(
        f"**{len(rows)}** systems checked against **{len(rules)}** rules "
        f"— **{failed_count}** failed findings."
    )

st.subheader("Category breakdown")
cat_df = pd.DataFrame(
    [{"Category": c.category, "Score": c.score, "Failed": c.failed, "Total": c.total} for c in result.categories]
)
st.bar_chart(cat_df.set_index("Category")["Score"])
st.dataframe(cat_df, hide_index=True, use_container_width=True)

st.subheader("Remediation checklist")
if report_data["remediation"]:
    rem_df = pd.DataFrame(report_data["remediation"]).rename(
        columns={
            "severity": "Severity",
            "rule_id": "Rule",
            "category": "Category",
            "section_ref": "Section",
            "affected_rows": "Rows affected",
            "description": "Issue",
            "remediation": "Remediation",
        }
    )

    def _highlight_severity(value: object) -> str | None:
        color = SEVERITY_COLORS.get(str(value).lower())
        return f"background-color: {color}; color: white" if color else None

    st.dataframe(
        rem_df.style.map(_highlight_severity, subset=["Severity"]),
        hide_index=True,
        use_container_width=True,
    )
else:
    st.success("No failed findings — nothing to remediate.")

with NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
    render_report(result, rules, tmp_pdf.name)
    pdf_bytes = Path(tmp_pdf.name).read_bytes()

st.download_button(
    "Download PDF report", data=pdf_bytes, file_name="dpdp_report.pdf", mime="application/pdf", type="primary"
)
