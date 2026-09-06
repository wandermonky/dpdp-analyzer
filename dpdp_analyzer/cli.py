"""Typer CLI: `dpdp-check inventory.csv --out report.pdf --rules rules/dpdp_v1.yaml`."""
from __future__ import annotations

import json
from pathlib import Path

import typer

from dpdp_analyzer.engine import evaluate
from dpdp_analyzer.inventory import load_inventory
from dpdp_analyzer.report import render_report, render_report_json
from dpdp_analyzer.rules import load_rules
from dpdp_analyzer.scoring import score

app = typer.Typer(add_completion=False, help="Score a data-processing inventory against the DPDP Act/Rules.")


@app.command()
def check(
    inventory_path: Path = typer.Argument(..., help="CSV/XLSX data-processing inventory to check."),  # noqa: B008
    out: Path = typer.Option(Path("report.pdf"), "--out", help="Output PDF path. A matching .json is written alongside it."),  # noqa: B008
    rules_path: Path = typer.Option(Path("rules/dpdp_v1.yaml"), "--rules", help="YAML rule pack to check against."),  # noqa: B008
) -> None:
    """Validate an inventory, run it through the rule pack, and write a gap report."""
    if not rules_path.exists():
        typer.echo(f"Rule pack not found: {rules_path}", err=True)
        raise typer.Exit(code=1)
    if not inventory_path.exists():
        typer.echo(f"Inventory file not found: {inventory_path}", err=True)
        raise typer.Exit(code=1)

    rules = load_rules(rules_path)
    rows, errors = load_inventory(inventory_path)

    if errors:
        typer.echo("Inventory validation issues:", err=True)
        for error in errors:
            typer.echo(f"  - {error}", err=True)
        if not rows:
            typer.echo("No valid rows to check. Aborting.", err=True)
            raise typer.Exit(code=1)

    findings = evaluate(rows, rules)
    result = score(findings)

    render_report(result, rules, out)
    json_path = out.with_suffix(".json")
    json_path.write_text(json.dumps(render_report_json(result, rules), indent=2))

    typer.echo(f"Readiness score: {result.overall_score}/100")
    typer.echo("Top remediation items:")
    for item in result.remediation[:3]:
        typer.echo(f"  [{item.severity.upper()}] {item.rule_id} ({item.section_ref}) - affects {item.affected_rows} row(s)")
    typer.echo(f"Report written to {out} and {json_path}")


if __name__ == "__main__":
    app()
