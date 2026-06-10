"""Generate simulated hotel operations data for the analytics dashboard.

The script creates CSV files that mirror common ERP-style hotel operations
entities: bookings, invoices, accounts receivable, expenses, employee shifts,
and daily sales. It intentionally uses only the Python standard library so the
sample data can be generated before installing analysis dependencies.
"""

from __future__ import annotations

import argparse
import csv
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


@dataclass(frozen=True)
class HotelConfig:
    """Business assumptions used to generate the sample dataset."""

    rooms_available: int = 120
    start_date: date = date(2025, 1, 1)
    end_date: date = date(2025, 12, 31)
    seed: int = 42


ROOM_TYPES = {
    "Standard": 11_000,
    "Deluxe": 16_000,
    "Suite": 28_000,
    "Family": 22_000,
}
ROOM_TYPE_WEIGHTS = [0.48, 0.29, 0.08, 0.15]
REVENUE_CATEGORIES = ["Rooms", "Food & Beverage", "Spa", "Events", "Parking"]
DEPARTMENTS = ["Rooms", "Food & Beverage", "Housekeeping", "Maintenance", "Sales", "Admin"]
PAYMENT_TERMS = [15, 30, 45]
CUSTOMER_SEGMENTS = ["Corporate", "Leisure", "Travel Agency", "Event Group"]
CUSTOMER_SEGMENT_WEIGHTS = [0.32, 0.42, 0.18, 0.08]


def daterange(start_date: date, end_date: date):
    """Yield dates from start_date through end_date."""
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += timedelta(days=1)


def month_start_dates(start_date: date, end_date: date) -> list[date]:
    """Return first day of each month in the configured period."""
    months: list[date] = []
    current_month = date(start_date.year, start_date.month, 1)
    while current_month <= end_date:
        months.append(current_month)
        if current_month.month == 12:
            current_month = date(current_month.year + 1, 1, 1)
        else:
            current_month = date(current_month.year, current_month.month + 1, 1)
    return months


def seasonality_factor(business_date: date) -> float:
    """Return a demand multiplier for Aomori-style seasonal travel patterns."""
    if business_date.month in {7, 8}:
        return 1.35
    if business_date.month in {1, 2, 12}:
        return 1.15
    if business_date.month in {4, 5, 10}:
        return 1.05
    return 0.90


def weighted_choice(options: list[str], weights: list[float]) -> str:
    """Return one option using the supplied probability weights."""
    return random.choices(options, weights=weights, k=1)[0]


def build_bookings(config: HotelConfig) -> list[dict[str, object]]:
    """Create simulated room reservations with realistic stay lengths and rates."""
    rows: list[dict[str, object]] = []
    booking_id = 1

    for stay_date in daterange(config.start_date, config.end_date):
        demand = int(config.rooms_available * 0.62 * seasonality_factor(stay_date))
        occupied_rooms = int(max(35, min(random.gauss(demand, 10), config.rooms_available)))

        for _ in range(occupied_rooms):
            room_type = weighted_choice(list(ROOM_TYPES), ROOM_TYPE_WEIGHTS)
            stay_length = weighted_choice(["1", "2", "3", "4", "5"], [0.35, 0.30, 0.20, 0.10, 0.05])
            check_out = stay_date + timedelta(days=int(stay_length))
            segment = weighted_choice(CUSTOMER_SEGMENTS, CUSTOMER_SEGMENT_WEIGHTS)
            rate_variance = random.gauss(1.0, 0.08)
            room_rate = round(ROOM_TYPES[room_type] * seasonality_factor(stay_date) * rate_variance, 0)

            rows.append(
                {
                    "booking_id": booking_id,
                    "customer_id": random.randint(1001, 1125),
                    "customer_segment": segment,
                    "check_in_date": stay_date.isoformat(),
                    "check_out_date": check_out.isoformat(),
                    "room_type": room_type,
                    "rooms_booked": 1,
                    "room_rate_jpy": max(room_rate, ROOM_TYPES[room_type] * 0.75),
                }
            )
            booking_id += 1

    return rows


def build_invoices(bookings: list[dict[str, object]]) -> list[dict[str, object]]:
    """Create invoice records linked to bookings."""
    invoices: list[dict[str, object]] = []

    for invoice_id, booking in enumerate(bookings, start=1):
        check_in_date = date.fromisoformat(str(booking["check_in_date"]))
        check_out_date = date.fromisoformat(str(booking["check_out_date"]))
        stay_nights = (check_out_date - check_in_date).days
        room_revenue = stay_nights * float(booking["room_rate_jpy"])
        ancillary_revenue = round(room_revenue * random.uniform(0.12, 0.38), 0)
        invoice_amount = room_revenue + ancillary_revenue
        payment_terms_days = random.choices(PAYMENT_TERMS, weights=[0.25, 0.55, 0.20], k=1)[0]
        due_date = check_out_date + timedelta(days=payment_terms_days)

        invoices.append(
            {
                "invoice_id": invoice_id,
                "booking_id": booking["booking_id"],
                "customer_id": booking["customer_id"],
                "invoice_date": check_out_date.isoformat(),
                "due_date": due_date.isoformat(),
                "payment_terms_days": payment_terms_days,
                "room_revenue_jpy": round(room_revenue, 0),
                "ancillary_revenue_jpy": ancillary_revenue,
                "invoice_amount_jpy": round(invoice_amount, 0),
            }
        )

    return invoices


def build_accounts_receivable(invoices: list[dict[str, object]]) -> list[dict[str, object]]:
    """Create payment status and outstanding-balance records for each invoice."""
    rows: list[dict[str, object]] = []
    as_of_date = date(2025, 12, 31)

    for invoice in invoices:
        due_date = date.fromisoformat(str(invoice["due_date"]))
        invoice_amount = float(invoice["invoice_amount_jpy"])
        late_probability = 0.18 if invoice_amount < 80_000 else 0.28
        is_late = random.random() < late_probability
        is_unpaid = due_date > as_of_date or (is_late and random.random() < 0.45)

        if is_unpaid:
            payment_date = ""
            amount_paid = 0 if random.random() < 0.75 else round(invoice_amount * random.uniform(0.25, 0.70), 0)
        else:
            delay_days = int(random.gauss(4 if not is_late else 28, 9))
            payment_date = (due_date + timedelta(days=max(delay_days, -5))).isoformat()
            amount_paid = invoice_amount

        outstanding_balance = max(invoice_amount - amount_paid, 0)
        days_past_due = max((as_of_date - due_date).days, 0) if outstanding_balance > 0 else 0

        rows.append(
            {
                "ar_id": len(rows) + 1,
                "invoice_id": invoice["invoice_id"],
                "customer_id": invoice["customer_id"],
                "payment_date": payment_date,
                "amount_paid_jpy": amount_paid,
                "outstanding_balance_jpy": outstanding_balance,
                "days_past_due": days_past_due,
                "payment_status": "Open" if outstanding_balance > 0 else "Paid",
            }
        )

    return rows


def build_department_expenses(config: HotelConfig) -> list[dict[str, object]]:
    """Create monthly departmental cost records."""
    base_costs = {
        "Rooms": 5_500_000,
        "Food & Beverage": 4_200_000,
        "Housekeeping": 3_300_000,
        "Maintenance": 1_600_000,
        "Sales": 1_250_000,
        "Admin": 1_900_000,
    }
    rows: list[dict[str, object]] = []

    for month in month_start_dates(config.start_date, config.end_date):
        for department, base_cost in base_costs.items():
            cost = base_cost * seasonality_factor(month) * random.gauss(1.0, 0.06)
            rows.append(
                {
                    "expense_id": len(rows) + 1,
                    "expense_month": month.isoformat(),
                    "department": department,
                    "expense_category": "Labor" if department in {"Housekeeping", "Rooms"} else "Operating",
                    "amount_jpy": round(cost, 0),
                }
            )

    return rows


def build_employee_shifts(config: HotelConfig) -> list[dict[str, object]]:
    """Create staffing hours by department and date."""
    rows: list[dict[str, object]] = []

    for work_date in daterange(config.start_date, config.end_date):
        for department in DEPARTMENTS:
            base_hours = 60 if department in {"Rooms", "Housekeeping", "Food & Beverage"} else 24
            hours = base_hours * seasonality_factor(work_date) * random.gauss(1.0, 0.10)
            rows.append(
                {
                    "shift_id": len(rows) + 1,
                    "work_date": work_date.isoformat(),
                    "department": department,
                    "labor_hours": round(max(hours, 8), 2),
                    "scheduled_staff": int(max(round(hours / 8), 1)),
                }
            )

    return rows


def build_daily_sales(bookings: list[dict[str, object]]) -> list[dict[str, object]]:
    """Create daily sales by revenue category."""
    room_sales_by_date: dict[str, float] = {}
    for booking in bookings:
        stay_date = str(booking["check_in_date"])
        room_sales_by_date[stay_date] = room_sales_by_date.get(stay_date, 0) + float(booking["room_rate_jpy"])

    rows: list[dict[str, object]] = []
    for sales_date, room_sales in sorted(room_sales_by_date.items()):
        category_amounts = {
            "Rooms": room_sales,
            "Food & Beverage": room_sales * random.uniform(0.18, 0.32),
            "Spa": room_sales * random.uniform(0.03, 0.09),
            "Events": room_sales * random.uniform(0.02, 0.18),
            "Parking": room_sales * random.uniform(0.01, 0.04),
        }
        for category in REVENUE_CATEGORIES:
            rows.append(
                {
                    "sales_id": len(rows) + 1,
                    "sales_date": sales_date,
                    "revenue_category": category,
                    "amount_jpy": round(category_amounts[category], 0),
                }
            )

    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write a list of dictionaries to a CSV file."""
    if not rows:
        raise ValueError(f"No rows available for {path}")

    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def generate_dataset(output_dir: Path, config: HotelConfig) -> None:
    """Generate all CSV files into the requested output directory."""
    random.seed(config.seed)
    output_dir.mkdir(parents=True, exist_ok=True)

    bookings = build_bookings(config)
    invoices = build_invoices(bookings)
    datasets = {
        "bookings.csv": bookings,
        "invoices.csv": invoices,
        "accounts_receivable.csv": build_accounts_receivable(invoices),
        "department_expenses.csv": build_department_expenses(config),
        "employee_shifts.csv": build_employee_shifts(config),
        "daily_sales.csv": build_daily_sales(bookings),
    }

    for filename, rows in datasets.items():
        write_csv(output_dir / filename, rows)

    print(f"Generated {len(datasets)} files in {output_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate simulated hotel operations CSV data.")
    parser.add_argument("--output-dir", type=Path, default=Path("data/raw"), help="Directory for generated CSV files.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for repeatable results.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate_dataset(args.output_dir, HotelConfig(seed=args.seed))


if __name__ == "__main__":
    main()
