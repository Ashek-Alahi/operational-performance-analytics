from pathlib import Path
import subprocess
import sys

RAW_FILES = [
    "bookings.csv",
    "invoices.csv",
    "accounts_receivable.csv",
    "department_expenses.csv",
    "employee_shifts.csv",
    "daily_sales.csv",
]

OUTPUT_FILES = [
    "monthly_kpis.csv",
    "revenue_category_summary.csv",
    "department_cost_summary.csv",
    "ar_aging_summary.csv",
    "customer_collection_priority.csv",
    "executive_summary.md",
]


def run_command(args, cwd: Path) -> None:
    subprocess.run([sys.executable, *args], cwd=cwd, check=True)


def test_data_generation_creates_expected_files(tmp_path: Path) -> None:
    repo = Path(__file__).resolve().parents[1]
    raw_dir = tmp_path / "raw"
    run_command(["data/generate_data.py", "--output-dir", str(raw_dir)], repo)
    for filename in RAW_FILES:
        assert (raw_dir / filename).exists()


def test_generated_csvs_contain_required_columns(tmp_path: Path) -> None:
    repo = Path(__file__).resolve().parents[1]
    raw_dir = tmp_path / "raw"
    run_command(["data/generate_data.py", "--output-dir", str(raw_dir)], repo)
    assert (raw_dir / "bookings.csv").read_text().splitlines()[0].split(",") == [
        "booking_id", "customer_id", "customer_segment", "check_in_date", "check_out_date", "room_type", "rooms_booked", "room_rate_jpy"
    ]
    assert "invoice_id,booking_id,customer_id" in (raw_dir / "invoices.csv").read_text().splitlines()[0]


def test_analysis_generation_and_validation_pass(tmp_path: Path) -> None:
    repo = Path(__file__).resolve().parents[1]
    raw_dir = tmp_path / "raw"
    output_dir = tmp_path / "outputs"
    dashboard_path = tmp_path / "dashboard" / "executive_dashboard.html"
    run_command(["data/generate_data.py", "--output-dir", str(raw_dir)], repo)
    run_command([
        "analysis/generate_results.py",
        "--data-dir", str(raw_dir),
        "--output-dir", str(output_dir),
        "--dashboard-path", str(dashboard_path),
    ], repo)
    for filename in OUTPUT_FILES:
        assert (output_dir / filename).exists()
    assert dashboard_path.exists()
    run_command(["analysis/validate_outputs.py", "--raw-dir", str(raw_dir), "--output-dir", str(output_dir)], repo)
