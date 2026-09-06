# DPDP Gap-Analyzer & Report Generator

A tool that takes a data-processing inventory (a spreadsheet describing what
personal data your systems collect and how it's handled) and scores it against
the Digital Personal Data Protection Act 2023 and the DPDP Rules 2025. It
outputs a 0-100 readiness score, a per-category breakdown, and a PDF/JSON gap
report with a remediation checklist ranked by severity.

> **Not legal advice.** This tool encodes a plain-language reading of the
> DPDP Act and Rules for engineering purposes. Every rule in `rules/dpdp_v1.yaml`
> is currently marked `status: draft` — none have been cross-checked against
> the bare Act/Rules text by a qualified professional. Verify every finding
> against the current DPDP Act and Rules before acting on it. This is a
> portfolio/educational project, not certified compliance software.

## What it does

1. **Input** — reads a CSV/XLSX data-processing inventory (one row per
   system/data flow).
2. **Validate** — checks every row against a Pydantic schema; a bad file
   produces readable per-row errors instead of crashing.
3. **Evaluate** — runs 20 DPDP rules (consent, notice, data-principal rights,
   breach notification, Significant Data Fiduciary obligations) against every
   row.
4. **Score** — a severity-weighted 0-100 readiness score, broken down by
   category.
5. **Report** — a client-presentable PDF (+ matching JSON) with the score,
   category breakdown, and a remediation checklist sorted by severity, each
   item citing its Act/Rules section.

## Install

```
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

PDF generation uses [WeasyPrint](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html),
which needs the Pango/GObject native libraries. On Windows:

1. Install [MSYS2](https://www.msys2.org/#installation) (default options).
2. In the **MSYS2 MinGW 64-bit** shell: `pacman -S mingw-w64-x86_64-pango`
3. If WeasyPrint still can't find the libraries, set:
   `set WEASYPRINT_DLL_DIRECTORIES=C:\msys64\mingw64\bin`
   (`dpdp_analyzer/report.py` already sets this as a default if you installed
   MSYS2 to its default location, so most Windows users don't need to.)

On macOS/Linux, follow WeasyPrint's own install docs (usually a single
`brew`/`apt` package).

## Usage

```
dpdp-check dpdp_analyzer/sample_inventory.csv --out reports/demo.pdf --rules rules/dpdp_v1.yaml
```

Sample output, run against the bundled synthetic inventory:

```
Readiness score: 80.1/100
Top remediation items:
  [CRITICAL] consent-01 (S. 6) - affects 3 row(s)
  [CRITICAL] breach-02 (S. 8(6)) - affects 3 row(s)
  [CRITICAL] consent-02 (S. 9) - affects 2 row(s)
Report written to reports\demo.pdf and reports\demo.json
```

This writes `reports/demo.pdf` (the client-facing report) and
`reports/demo.json` (the same data, machine-readable).

### Web UI (optional)

```
pip install -e ".[ui]"
streamlit run streamlit_app.py
```

Upload a CSV, see the score and remediation table, download the PDF — same
pipeline, no separate logic.

## Rule pack coverage

`rules/dpdp_v1.yaml` has 20 rules across 5 categories. All are `status: draft`.

| Category | Rules | What's covered |
|---|---|---|
| Consent | 4 | Verifiable consent, parental/guardian consent for children/disabled persons, consent logging, withdrawal |
| Notice | 4 | Notice given, itemized, DPO contact included, grievance/withdrawal links included |
| Data-principal rights | 4 | Access, correction/erasure, published grievance mechanism, 90-day resolution SLA |
| Breach notification | 4 | Security safeguards (encryption for sensitive categories), breach process defined, individual notification, 72-hour report |
| Significant Data Fiduciary | 4 | India-based DPO, independent auditor, DPIA, Board reporting |

**Not covered / TODO:**
- Cross-border transfer restrictions (S. 16) — the inventory tracks the flag but no rule evaluates it yet.
- Consent Manager registration/obligations.
- Data retention limits beyond what's captured in `retention_period_days`.
- Penalty amount estimation (the Act's penalty schedule isn't modeled — only severity weighting).
- Section numbers are a first-pass reading and need legal review before this pack is used on anything but synthetic test data.

## Testing

```
pytest --cov=dpdp_analyzer
ruff check .
mypy dpdp_analyzer streamlit_app.py
```

Current status: 61 tests, 98% coverage on `dpdp_analyzer/`, `ruff` and `mypy`
both clean.

## Project layout

```
dpdp_analyzer/     package: inventory schema+loader, rule schema+loader,
                    evaluation engine, scoring, report rendering, CLI
rules/              YAML rule packs (dated, e.g. dpdp_v1.yaml)
reports/templates/  Jinja2 HTML report template
tests/              pytest, covering every rule (pass + fail case) and
                    the loader/engine/scoring/report/CLI pipeline
streamlit_app.py    optional web UI
```

## Limitations

This is a portfolio/educational project built against synthetic data only. It
is **not** certified compliance software and should never be pointed at real
employer or client data. Before relying on it for anything real:

- Have the rule pack's `section_ref` citations reviewed by someone qualified
  to read the DPDP Act and Rules.
- Extend the inventory schema and rule pack to cover what's listed as
  not-covered above.
- The DPDP Rules were notified 13 Nov 2025 and are phasing in over time
  (Consent Manager registration closes Nov 2026; full penalty enforcement
  from May 2027) — this tool doesn't yet distinguish "not enforceable yet"
  from "non-compliant."
