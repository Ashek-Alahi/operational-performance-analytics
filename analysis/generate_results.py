"""Create portfolio-ready KPI outputs from the generated hotel CSV files.

The project can be reviewed without a live PostgreSQL or Power BI installation by
running this script after ``data/generate_data.py``. It calculates the same core
business metrics used by the SQL views and exports compact CSV/Markdown/HTML
artifacts for GitHub reviewers.
"""

from __future__ import annotations

import argparse
import csv
import html
from calendar import monthrange
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

ROOMS_AVAILABLE = 120


@dataclass(frozen=True)
class MonthlyKpi:
    """Monthly operational and financial KPI row."""

    month: str
    revenue_jpy: float
    operating_cost_jpy: float
    operating_profit_jpy: float
    profit_margin_pct: float
    occupied_room_nights: int
    available_room_nights: int
    occupancy_rate_pct: float
    adr_jpy: float
    labor_hours: float
    revenue_per_labor_hour_jpy: float


def read_csv(data_dir: Path, filename: str) -> list[dict[str, str]]:
    """Read a generated CSV file as dictionaries."""
    path = data_dir / filename
    with path.open(newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def month_key(date_text: str) -> str:
    """Return YYYY-MM from an ISO date string."""
    return date_text[:7]


def month_label(month: str) -> str:
    """Return a readable month label from YYYY-MM."""
    return datetime.strptime(month, "%Y-%m").strftime("%B %Y")


def yen(value: float) -> str:
    """Format Japanese yen without decimal places."""
    return f"¥{value:,.0f}"


def pct(value: float) -> str:
    """Format a percentage with one decimal place."""
    return f"{value:.1f}%"


def write_rows(path: Path, rows: Iterable[dict[str, object]]) -> None:
    """Write dictionaries to CSV."""
    rows = list(rows)
    if not rows:
        raise ValueError(f"No rows to write for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_monthly_kpis(data_dir: Path) -> list[MonthlyKpi]:
    """Calculate monthly revenue, cost, occupancy, ADR, and labor KPIs."""
    bookings = read_csv(data_dir, "bookings.csv")
    invoices = read_csv(data_dir, "invoices.csv")
    daily_sales = read_csv(data_dir, "daily_sales.csv")
    expenses = read_csv(data_dir, "department_expenses.csv")
    shifts = read_csv(data_dir, "employee_shifts.csv")

    revenue_by_month: defaultdict[str, float] = defaultdict(float)
    cost_by_month: defaultdict[str, float] = defaultdict(float)
    labor_by_month: defaultdict[str, float] = defaultdict(float)
    occupied_room_nights_by_month: defaultdict[str, int] = defaultdict(int)
    room_revenue_by_month: defaultdict[str, float] = defaultdict(float)

    invoice_by_booking_id = {row["booking_id"]: row for row in invoices}

    for row in daily_sales:
        revenue_by_month[month_key(row["sales_date"])] += float(row["amount_jpy"])

    for row in expenses:
        cost_by_month[month_key(row["expense_month"])] += float(row["amount_jpy"])

    for row in shifts:
        labor_by_month[month_key(row["work_date"])] += float(row["labor_hours"])

    for booking in bookings:
        check_in = datetime.fromisoformat(booking["check_in_date"]).date()
        check_out = datetime.fromisoformat(booking["check_out_date"]).date()
        room_nights = (check_out - check_in).days * int(booking["rooms_booked"])
        month = check_in.strftime("%Y-%m")
        occupied_room_nights_by_month[month] += room_nights
        room_revenue_by_month[month] += float(invoice_by_booking_id[booking["booking_id"]]["room_revenue_jpy"])

    kpis: list[MonthlyKpi] = []
    for month in sorted(revenue_by_month):
        revenue = revenue_by_month[month]
        cost = cost_by_month[month]
        profit = revenue - cost
        year, month_number = [int(part) for part in month.split("-")]
        available_room_nights = ROOMS_AVAILABLE * monthrange(year, month_number)[1]
        occupied_room_nights = occupied_room_nights_by_month[month]
        occupancy_rate = occupied_room_nights / available_room_nights * 100
        adr = room_revenue_by_month[month] / occupied_room_nights
        labor_hours = labor_by_month[month]
        kpis.append(
            MonthlyKpi(
                month=month,
                revenue_jpy=revenue,
                operating_cost_jpy=cost,
                operating_profit_jpy=profit,
                profit_margin_pct=profit / revenue * 100,
                occupied_room_nights=occupied_room_nights,
                available_room_nights=available_room_nights,
                occupancy_rate_pct=occupancy_rate,
                adr_jpy=adr,
                labor_hours=labor_hours,
                revenue_per_labor_hour_jpy=revenue / labor_hours,
            )
        )
    return kpis


def build_ar_aging(data_dir: Path) -> list[dict[str, object]]:
    """Summarize accounts receivable into standard aging buckets."""
    bucket_order = ["Paid", "0-30 days", "31-60 days", "60+ days"]
    balances: defaultdict[str, float] = defaultdict(float)
    invoice_counts: Counter[str] = Counter()
    customer_sets: defaultdict[str, set[str]] = defaultdict(set)

    for row in read_csv(data_dir, "accounts_receivable.csv"):
        balance = float(row["outstanding_balance_jpy"])
        days_past_due = int(row["days_past_due"])
        if balance == 0:
            bucket = "Paid"
        elif days_past_due <= 30:
            bucket = "0-30 days"
        elif days_past_due <= 60:
            bucket = "31-60 days"
        else:
            bucket = "60+ days"
        balances[bucket] += balance
        invoice_counts[bucket] += 1
        customer_sets[bucket].add(row["customer_id"])

    return [
        {
            "aging_bucket": bucket,
            "invoice_count": invoice_counts[bucket],
            "customer_count": len(customer_sets[bucket]),
            "outstanding_balance_jpy": round(balances[bucket], 0),
        }
        for bucket in bucket_order
    ]


def build_category_summary(data_dir: Path) -> list[dict[str, object]]:
    """Summarize revenue by category."""
    revenue_by_category: defaultdict[str, float] = defaultdict(float)
    for row in read_csv(data_dir, "daily_sales.csv"):
        revenue_by_category[row["revenue_category"]] += float(row["amount_jpy"])
    total_revenue = sum(revenue_by_category.values())
    return [
        {
            "revenue_category": category,
            "revenue_jpy": round(revenue, 0),
            "revenue_share_pct": round(revenue / total_revenue * 100, 2),
        }
        for category, revenue in sorted(revenue_by_category.items(), key=lambda item: item[1], reverse=True)
    ]


def build_department_summary(data_dir: Path) -> list[dict[str, object]]:
    """Summarize annual cost by department."""
    cost_by_department: defaultdict[str, float] = defaultdict(float)
    for row in read_csv(data_dir, "department_expenses.csv"):
        cost_by_department[row["department"]] += float(row["amount_jpy"])
    total_cost = sum(cost_by_department.values())
    return [
        {
            "department": department,
            "cost_jpy": round(cost, 0),
            "cost_share_pct": round(cost / total_cost * 100, 2),
        }
        for department, cost in sorted(cost_by_department.items(), key=lambda item: item[1], reverse=True)
    ]


def build_customer_collection_priority(data_dir: Path) -> list[dict[str, object]]:
    """Rank customers by overdue collection risk."""
    customer_balance: defaultdict[str, float] = defaultdict(float)
    customer_over_60_count: Counter[str] = Counter()
    customer_oldest_days: defaultdict[str, int] = defaultdict(int)

    for row in read_csv(data_dir, "accounts_receivable.csv"):
        balance = float(row["outstanding_balance_jpy"])
        days_past_due = int(row["days_past_due"])
        if balance <= 0:
            continue
        customer_id = row["customer_id"]
        customer_balance[customer_id] += balance
        customer_oldest_days[customer_id] = max(customer_oldest_days[customer_id], days_past_due)
        if days_past_due > 60:
            customer_over_60_count[customer_id] += 1

    rows = [
        {
            "customer_id": customer_id,
            "total_outstanding_jpy": round(balance, 0),
            "invoices_over_60_days": customer_over_60_count[customer_id],
            "oldest_days_past_due": customer_oldest_days[customer_id],
        }
        for customer_id, balance in customer_balance.items()
    ]
    return sorted(rows, key=lambda row: row["total_outstanding_jpy"], reverse=True)[:15]


def export_monthly_kpis(kpis: list[MonthlyKpi], output_dir: Path) -> None:
    """Export monthly KPI CSV."""
    write_rows(
        output_dir / "monthly_kpis.csv",
        [
            {
                "month": kpi.month,
                "revenue_jpy": round(kpi.revenue_jpy, 0),
                "operating_cost_jpy": round(kpi.operating_cost_jpy, 0),
                "operating_profit_jpy": round(kpi.operating_profit_jpy, 0),
                "profit_margin_pct": round(kpi.profit_margin_pct, 2),
                "occupied_room_nights": kpi.occupied_room_nights,
                "available_room_nights": kpi.available_room_nights,
                "occupancy_rate_pct": round(kpi.occupancy_rate_pct, 2),
                "adr_jpy": round(kpi.adr_jpy, 0),
                "labor_hours": round(kpi.labor_hours, 2),
                "revenue_per_labor_hour_jpy": round(kpi.revenue_per_labor_hour_jpy, 0),
            }
            for kpi in kpis
        ],
    )


def write_executive_summary(
    output_dir: Path,
    kpis: list[MonthlyKpi],
    category_summary: list[dict[str, object]],
    ar_aging: list[dict[str, object]],
    department_summary: list[dict[str, object]],
) -> None:
    """Write Markdown findings for the README and portfolio review."""
    total_revenue = sum(kpi.revenue_jpy for kpi in kpis)
    total_cost = sum(kpi.operating_cost_jpy for kpi in kpis)
    total_profit = total_revenue - total_cost
    annual_margin = total_profit / total_revenue * 100
    peak_occupancy = max(kpis, key=lambda kpi: kpi.occupancy_rate_pct)
    best_margin = max(kpis, key=lambda kpi: kpi.profit_margin_pct)
    top_category = category_summary[0]
    top_department = department_summary[0]
    open_ar = sum(float(row["outstanding_balance_jpy"]) for row in ar_aging if row["aging_bucket"] != "Paid")
    over_60_ar = next(float(row["outstanding_balance_jpy"]) for row in ar_aging if row["aging_bucket"] == "60+ days")

    content = f"""# Executive KPI Findings

## Annual Results

| KPI | Result |
| --- | ---: |
| Total revenue | {yen(total_revenue)} |
| Operating cost | {yen(total_cost)} |
| Operating profit | {yen(total_profit)} |
| Profit margin | {pct(annual_margin)} |
| Outstanding receivables | {yen(open_ar)} |
| 60+ day receivables | {yen(over_60_ar)} |

## Business Findings

1. Peak occupancy occurred in **{month_label(peak_occupancy.month)}** at **{pct(peak_occupancy.occupancy_rate_pct)}**, confirming a clear seasonal demand peak.
2. The strongest profit-margin month was **{month_label(best_margin.month)}** at **{pct(best_margin.profit_margin_pct)}**, supported by high revenue and controlled cost growth.
3. **{top_category['revenue_category']}** was the largest revenue category at **{yen(float(top_category['revenue_jpy']))}**, representing **{top_category['revenue_share_pct']}%** of annual revenue.
4. **{top_department['department']}** was the highest-cost department at **{yen(float(top_department['cost_jpy']))}**, representing **{top_department['cost_share_pct']}%** of operating costs.
5. Receivables over 60 days totaled **{yen(over_60_ar)}**, which should be the first collection-management focus because it has the highest cash-risk profile.

## Recommended Management Actions

- Protect peak-season profitability by locking staffing plans and purchasing budgets before July and August.
- Use room-demand seasonality to review pricing floors for low-demand months.
- Prioritize collection calls for customers with 60+ day balances before normal monthly statement follow-up.
- Monitor Rooms and Food & Beverage costs monthly because they are the largest cost centers and have the greatest impact on margin.
"""
    (output_dir / "executive_summary.md").write_text(content, encoding="utf-8")


def write_dashboard_html(
    dashboard_path: Path,
    kpis: list[MonthlyKpi],
    category_summary: list[dict[str, object]],
    ar_aging: list[dict[str, object]],
) -> None:
    """Write a lightweight static dashboard preview for GitHub reviewers."""
    total_revenue = sum(kpi.revenue_jpy for kpi in kpis)
    total_cost = sum(kpi.operating_cost_jpy for kpi in kpis)
    total_profit = total_revenue - total_cost
    annual_margin = total_profit / total_revenue * 100
    peak_occupancy = max(kpis, key=lambda kpi: kpi.occupancy_rate_pct)
    open_ar = sum(float(row["outstanding_balance_jpy"]) for row in ar_aging if row["aging_bucket"] != "Paid")

    monthly_rows = "\n".join(
        f"<tr><td>{html.escape(month_label(kpi.month))}</td><td>{yen(kpi.revenue_jpy)}</td>"
        f"<td>{yen(kpi.operating_profit_jpy)}</td><td>{pct(kpi.profit_margin_pct)}</td>"
        f"<td>{pct(kpi.occupancy_rate_pct)}</td><td>{yen(kpi.adr_jpy)}</td></tr>"
        for kpi in kpis
    )
    category_rows = "\n".join(
        f"<tr><td>{html.escape(str(row['revenue_category']))}</td><td>{yen(float(row['revenue_jpy']))}</td>"
        f"<td>{row['revenue_share_pct']}%</td></tr>"
        for row in category_summary
    )
    ar_rows = "\n".join(
        f"<tr><td>{html.escape(str(row['aging_bucket']))}</td><td>{row['invoice_count']}</td>"
        f"<td>{row['customer_count']}</td><td>{yen(float(row['outstanding_balance_jpy']))}</td></tr>"
        for row in ar_aging
    )

    content = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Hotel Operations Performance Dashboard</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; color: #1f2937; background: #f3f4f6; }}
    header {{ background: #0f172a; color: white; padding: 28px 40px; }}
    main {{ padding: 28px 40px; }}
    .grid {{ display: grid; grid-template-columns: repeat(5, minmax(140px, 1fr)); gap: 16px; }}
    .card, section {{ background: white; border-radius: 14px; box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08); }}
    .card {{ padding: 18px; }}
    .label {{ color: #64748b; font-size: 13px; text-transform: uppercase; letter-spacing: .06em; }}
    .value {{ font-size: 24px; font-weight: 700; margin-top: 8px; }}
    section {{ margin-top: 22px; padding: 22px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid #e5e7eb; text-align: right; }}
    th:first-child, td:first-child {{ text-align: left; }}
    th {{ background: #f8fafc; color: #475569; }}
    .note {{ color: #64748b; }}
  </style>
</head>
<body>
  <header>
    <h1>Hotel Operations Performance Analytics</h1>
    <p>Static portfolio dashboard preview generated from the project's CSV dataset.</p>
  </header>
  <main>
    <div class="grid">
      <div class="card"><div class="label">Revenue</div><div class="value">{yen(total_revenue)}</div></div>
      <div class="card"><div class="label">Operating Profit</div><div class="value">{yen(total_profit)}</div></div>
      <div class="card"><div class="label">Profit Margin</div><div class="value">{pct(annual_margin)}</div></div>
      <div class="card"><div class="label">Peak Occupancy</div><div class="value">{pct(peak_occupancy.occupancy_rate_pct)}</div></div>
      <div class="card"><div class="label">Open AR</div><div class="value">{yen(open_ar)}</div></div>
    </div>
    <section>
      <h2>Monthly KPI Trend</h2>
      <p class="note">Use this table to validate Power BI cards and line charts.</p>
      <table><thead><tr><th>Month</th><th>Revenue</th><th>Operating Profit</th><th>Margin</th><th>Occupancy</th><th>ADR</th></tr></thead><tbody>{monthly_rows}</tbody></table>
    </section>
    <section>
      <h2>Revenue Category Mix</h2>
      <table><thead><tr><th>Category</th><th>Revenue</th><th>Share</th></tr></thead><tbody>{category_rows}</tbody></table>
    </section>
    <section>
      <h2>Accounts Receivable Aging</h2>
      <table><thead><tr><th>Bucket</th><th>Invoices</th><th>Customers</th><th>Outstanding</th></tr></thead><tbody>{ar_rows}</tbody></table>
    </section>
  </main>
</body>
</html>
"""
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard_path.write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description="Generate hotel portfolio KPI outputs.")
    parser.add_argument("--data-dir", type=Path, default=Path("data/raw"), help="Directory containing generated CSV files.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("analysis/outputs"),
        help="Directory for exported KPI summaries.",
    )
    parser.add_argument(
        "--dashboard-path",
        type=Path,
        default=Path("dashboard/executive_dashboard.html"),
        help="Path for the static HTML dashboard preview.",
    )
    return parser.parse_args()


def main() -> None:
    """Generate all analysis outputs."""
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    kpis = build_monthly_kpis(args.data_dir)
    category_summary = build_category_summary(args.data_dir)
    ar_aging = build_ar_aging(args.data_dir)
    department_summary = build_department_summary(args.data_dir)
    customer_collection_priority = build_customer_collection_priority(args.data_dir)

    export_monthly_kpis(kpis, args.output_dir)
    write_rows(args.output_dir / "revenue_category_summary.csv", category_summary)
    write_rows(args.output_dir / "ar_aging_summary.csv", ar_aging)
    write_rows(args.output_dir / "department_cost_summary.csv", department_summary)
    write_rows(args.output_dir / "customer_collection_priority.csv", customer_collection_priority)
    write_executive_summary(args.output_dir, kpis, category_summary, ar_aging, department_summary)
    write_dashboard_html(args.dashboard_path, kpis, category_summary, ar_aging)

    print(f"Generated KPI outputs in {args.output_dir}")
    print(f"Generated dashboard preview at {args.dashboard_path}")


if __name__ == "__main__":
    main()
