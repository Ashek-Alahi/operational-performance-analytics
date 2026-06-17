"""Validate generated hotel operations data and KPI outputs.

Run after:
    python data/generate_data.py --output-dir data/raw
    python analysis/generate_results.py
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

RAW_FILES = {
    "bookings.csv": {"booking_id", "customer_id", "customer_segment", "check_in_date", "check_out_date", "room_type", "rooms_booked", "room_rate_jpy"},
    "invoices.csv": {"invoice_id", "booking_id", "customer_id", "invoice_date", "due_date", "payment_terms_days", "room_revenue_jpy", "ancillary_revenue_jpy", "invoice_amount_jpy"},
    "accounts_receivable.csv": {"ar_id", "invoice_id", "customer_id", "payment_date", "amount_paid_jpy", "outstanding_balance_jpy", "days_past_due", "payment_status"},
    "department_expenses.csv": {"expense_id", "expense_month", "department", "expense_category", "amount_jpy"},
    "employee_shifts.csv": {"shift_id", "work_date", "department", "labor_hours", "scheduled_staff"},
    "daily_sales.csv": {"sales_id", "sales_date", "revenue_category", "amount_jpy"},
}

OUTPUT_FILES = {
    "monthly_kpis.csv": {"month", "revenue_jpy", "operating_cost_jpy", "operating_profit_jpy", "profit_margin_pct", "occupied_room_nights", "available_room_nights", "occupancy_rate_pct", "adr_jpy", "labor_hours", "revenue_per_labor_hour_jpy"},
    "revenue_category_summary.csv": {"revenue_category", "revenue_jpy", "revenue_share_pct"},
    "department_cost_summary.csv": {"department", "cost_jpy", "cost_share_pct"},
    "ar_aging_summary.csv": {"aging_bucket", "invoice_count", "customer_count", "outstanding_balance_jpy"},
    "customer_collection_priority.csv": {"customer_id", "total_outstanding_jpy", "invoices_over_60_days", "oldest_days_past_due"},
}

REQUIRED_AGING_BUCKETS = {"Paid", "0-30 days", "31-60 days", "60+ days"}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def require(condition: bool, message: str, failures: list[str]) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {message}")
    if not condition:
        failures.append(message)


def validate_file_group(base_dir: Path, expected_files: dict[str, set[str]], failures: list[str]) -> dict[str, list[dict[str, str]]]:
    loaded: dict[str, list[dict[str, str]]] = {}
    for filename, required_columns in expected_files.items():
        path = base_dir / filename
        require(path.exists(), f"{path} exists", failures)
        if not path.exists():
            continue
        rows = read_rows(path)
        loaded[filename] = rows
        columns = set(rows[0]) if rows else set()
        require(bool(rows), f"{path} has rows", failures)
        require(required_columns.issubset(columns), f"{path} contains required columns", failures)
    return loaded


def validate(raw_dir: Path, output_dir: Path) -> bool:
    print("Hotel Operations Performance Analytics validation report")
    print(f"Raw data directory: {raw_dir}")
    print(f"Output directory: {output_dir}\n")
    failures: list[str] = []

    raw = validate_file_group(raw_dir, RAW_FILES, failures)
    outputs = validate_file_group(output_dir, OUTPUT_FILES, failures)

    if raw:
        require(len(raw.get("bookings.csv", [])) > 1_000, "bookings row count is reasonable", failures)
        require(len(raw.get("invoices.csv", [])) == len(raw.get("accounts_receivable.csv", [])), "one AR row exists per invoice", failures)
        invoice_ids = {row["invoice_id"] for row in raw.get("invoices.csv", [])}
        ar_invoice_ids = {row["invoice_id"] for row in raw.get("accounts_receivable.csv", [])}
        require(ar_invoice_ids.issubset(invoice_ids), "AR invoice IDs connect to invoices", failures)
        total_revenue = sum(float(row["amount_jpy"]) for row in raw.get("daily_sales.csv", []))
        total_cost = sum(float(row["amount_jpy"]) for row in raw.get("department_expenses.csv", []))
        require(total_revenue > 0, "total revenue is positive", failures)
        require(total_cost > 0, "total cost is positive", failures)
        require(all(float(row["amount_jpy"]) >= 0 for row in raw.get("daily_sales.csv", [])), "no negative revenue", failures)
        require(all(float(row["labor_hours"]) >= 0 for row in raw.get("employee_shifts.csv", [])), "no negative labor hours", failures)

    monthly = outputs.get("monthly_kpis.csv", [])
    if monthly:
        require(len(monthly) == 12, "monthly KPI table has 12 months", failures)
        for row in monthly:
            revenue = float(row["revenue_jpy"])
            cost = float(row["operating_cost_jpy"])
            expected_margin = round((revenue - cost) / revenue * 100, 2)
            actual_margin = float(row["profit_margin_pct"])
            require(abs(expected_margin - actual_margin) <= 0.01, f"profit margin is valid for {row['month']}", failures)

    ar_aging = outputs.get("ar_aging_summary.csv", [])
    if ar_aging:
        buckets = {row["aging_bucket"] for row in ar_aging}
        require(REQUIRED_AGING_BUCKETS.issubset(buckets), "AR aging buckets exist", failures)

    print("\nValidation result:", "PASS" if not failures else "FAIL")
    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
    return not failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate generated hotel analytics files.")
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--output-dir", type=Path, default=Path("analysis/outputs"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sys.exit(0 if validate(args.raw_dir, args.output_dir) else 1)


if __name__ == "__main__":
    main()
