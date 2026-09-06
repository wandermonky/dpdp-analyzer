from pathlib import Path

from typer.testing import CliRunner

from dpdp_analyzer.cli import app

RULES_PATH = Path(__file__).parent.parent / "rules" / "dpdp_v1.yaml"
SAMPLE = Path(__file__).parent.parent / "dpdp_analyzer" / "sample_inventory.csv"

runner = CliRunner()


def test_help_exits_zero():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "check" in result.output.lower()


def test_check_on_sample_inventory_writes_report_and_prints_summary(tmp_path):
    out_pdf = tmp_path / "report.pdf"

    result = runner.invoke(
        app, [str(SAMPLE), "--out", str(out_pdf), "--rules", str(RULES_PATH)]
    )

    assert result.exit_code == 0
    assert "Readiness score" in result.output
    assert out_pdf.exists()
    assert out_pdf.with_suffix(".json").exists()


def test_check_reports_missing_file_without_a_stack_trace(tmp_path):
    result = runner.invoke(
        app, [str(tmp_path / "does_not_exist.csv"), "--out", str(tmp_path / "report.pdf"), "--rules", str(RULES_PATH)]
    )

    assert result.exit_code != 0
    assert "not found" in result.output.lower()
    assert "Traceback" not in result.output


def test_check_exits_nonzero_when_inventory_has_no_valid_rows(tmp_path):
    broken_csv = tmp_path / "broken.csv"
    broken_csv.write_text("not_a_real_column\nfoo\n")

    result = runner.invoke(
        app, [str(broken_csv), "--out", str(tmp_path / "report.pdf"), "--rules", str(RULES_PATH)]
    )

    assert result.exit_code != 0
