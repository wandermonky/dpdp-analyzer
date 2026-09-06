# DPDP Gap-Analyzer & Report Generator

A tool that scores a data-processing inventory against the Digital Personal Data
Protection Act 2023 and DPDP Rules 2025, producing a gap report and remediation
checklist.

## Non-negotiables

- **Not legal advice.** Every rule mapping is a draft until verified against the
  bare Act/Rules text. The disclaimer ships on every generated report and in the
  README, unchanged.
- **Synthetic data only.** Never feed this tool real inventories from an employer
  or client. Build and test entirely on fabricated data.
- **Every rule cites a source.** No rule enters `rules/*.yaml` without a
  `section_ref`. Anything unverified is marked `status: draft`.
- **Version the law, not just the code.** Rule packs are dated files
  (`dpdp_v1.yaml`). Each rule carries `effective_from`.

## Architecture

Five stages, each independently testable:

1. Input — data inventory (CSV/XLSX)
2. Validate — schema check (Pydantic)
3. Evaluate — rule pack engine
4. Score — severity-weighted gap score
5. Report — Jinja2 + WeasyPrint PDF (+ JSON)

## Stack

Python 3.11+, pandas, pydantic v2, pyyaml, jinja2 + weasyprint, typer (CLI),
pytest, ruff + mypy, streamlit (optional UI, built last).

## Layout

- `dpdp_analyzer/` — package (loader, engine, scoring, report, cli)
- `rules/` — YAML rule packs
- `tests/` — pytest, one test per rule minimum
- `reports/templates/` — Jinja2 HTML report templates

## Build phases

Work one phase at a time. Don't start the next phase until its "Definition of
done" is actually true. See DPDP_worksheet.pdf for full phase specs (0–7):
Scaffold → Rule pack → Input schema/validator → Rule-evaluation engine → Gap
scoring → Report generator → CLI/Streamlit → Docs & release.
