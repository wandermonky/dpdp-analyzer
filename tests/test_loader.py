from pathlib import Path

from dpdp_analyzer.inventory import load_inventory

SAMPLE = Path(__file__).parent.parent / "dpdp_analyzer" / "sample_inventory.csv"

VALID_HEADER = (
    "system_name,data_category,purpose,consent_captured,retention_period_days,"
    "cross_border_transfer,encryption_at_rest,is_child_or_disabled_data,"
    "parental_consent_captured,consent_log_maintained,consent_withdrawal_available,"
    "notice_provided,notice_itemized,notice_has_dpo_contact,notice_has_grievance_link,"
    "rights_access_enabled,rights_correction_erasure_enabled,grievance_mechanism_published,"
    "grievance_avg_resolution_days,breach_notification_process_defined,"
    "breach_notify_individuals_without_delay,breach_report_72h_filed,"
    "is_significant_data_fiduciary,dpo_appointed_india_based,independent_auditor_appointed,"
    "dpia_conducted,sdf_reporting_to_board"
)
VALID_ROW = (
    "CustomerCRM,contact_info,customer_support,true,365,false,true,false,false,true,true,"
    "true,true,true,true,true,true,true,30,true,true,true,false,false,false,false,false"
)


def test_valid_sample_inventory_loads_with_no_errors():
    rows, errors = load_inventory(SAMPLE)
    assert len(rows) == 12
    assert errors == []


def test_missing_column_fails_with_one_clear_message(tmp_path):
    bad_header = VALID_HEADER.replace("encryption_at_rest,", "")
    bad_row = VALID_ROW.replace("true,false,true,", "true,false,")
    path = tmp_path / "missing_column.csv"
    path.write_text(f"{bad_header}\n{bad_row}\n")

    rows, errors = load_inventory(path)

    assert rows == []
    assert len(errors) == 1
    assert "encryption_at_rest" in errors[0]


def test_bad_value_in_one_row_does_not_kill_the_run(tmp_path):
    bad_row = VALID_ROW.replace("true,365", "maybe,365", 1)
    path = tmp_path / "bad_value.csv"
    path.write_text(f"{VALID_HEADER}\n{VALID_ROW}\n{bad_row}\n")

    rows, errors = load_inventory(path)

    assert len(rows) == 1
    assert len(errors) == 1
    assert "Row 3" in errors[0]
