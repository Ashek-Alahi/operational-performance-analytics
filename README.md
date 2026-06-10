# Hotel Operations Performance Analytics Dashboard

![Project Status](https://img.shields.io/badge/status-complete-brightgreen)
![Tools](https://img.shields.io/badge/tools-Python%20%7C%20PostgreSQL%20%7C%20Power%20BI-blue)
![Domain](https://img.shields.io/badge/domain-Hospitality%20Analytics-green)

**Tools:** Python · PostgreSQL · SQL · Power BI-ready outputs  
**Domain:** Hospitality · Operational Analytics · Financial Analytics · ERP-style reporting  
**Business Context:** Hotel operations, revenue, cost, labor, and accounts receivable analytics  
**Currency:** Japanese yen (JPY)

---

## Executive Summary

This is a completed portfolio analytics project for a hotel/resort management scenario. It simulates ERP-style operational and finance data, provides a PostgreSQL schema and reporting views, calculates business KPIs, exports analysis-ready result tables, and includes a static dashboard preview for GitHub review.

The project is designed to show how an accountant, ERP analyst, or business analyst can connect operational activity to financial performance: occupancy, ADR, revenue mix, department costs, labor productivity, profit margin, and receivables aging.

---

## Business Problem

Hotel managers often review revenue, costs, labor, and receivables in separate reports. This makes it difficult to answer practical management questions quickly:

- Which months drive the highest occupancy and profit?
- Which revenue categories create the most value?
- Which departments create the largest cost pressure?
- Are labor hours aligned with seasonal demand?
- Which customers and aging buckets require collection action first?

This project consolidates those topics into one analytics model and dashboard-ready output layer.

---

## Completed Results

The repository already includes generated data and KPI output files, so reviewers can inspect the finished project without first configuring PostgreSQL or Power BI.

| Result Area | Output |
| --- | --- |
| Generated ERP-style CSV data | `data/raw/*.csv` |
| Monthly executive KPI table | `analysis/outputs/monthly_kpis.csv` |
| Revenue category summary | `analysis/outputs/revenue_category_summary.csv` |
| Department cost summary | `analysis/outputs/department_cost_summary.csv` |
| Accounts receivable aging | `analysis/outputs/ar_aging_summary.csv` |
| Customer collection priority list | `analysis/outputs/customer_collection_priority.csv` |
| Written business findings | `analysis/outputs/executive_summary.md` |
| Static dashboard preview | `dashboard/executive_dashboard.html` |
| Power BI DAX measures | `dashboard/power_bi_measures.md` |

---

## Key Findings From the Generated Dataset

| KPI | Result | Business Meaning |
| --- | ---: | --- |
| Total revenue | ¥356,310,662 | Annual simulated hotel operating revenue |
| Operating cost | ¥230,697,822 | Annual department operating cost |
| Operating profit | ¥125,612,840 | Revenue remaining after operating costs |
| Profit margin | 35.3% | Overall operating profitability |
| Peak occupancy month | July 2025 at 94.7% | Strongest seasonal demand period |
| Strongest margin month | July 2025 at 49.6% | Best month for profit conversion |
| Largest revenue category | Rooms: ¥248,583,661 | Core revenue driver, 69.77% of revenue |
| Largest cost department | Rooms: ¥73,264,250 | Highest cost center, 31.76% of cost |
| Outstanding receivables | ¥106,746,012 | Cash still to be collected |
| 60+ day receivables | ¥43,948,435 | Highest collection-risk bucket |

### Management Recommendations

1. **Protect July and August profitability** by finalizing staffing and procurement plans before peak season.
2. **Review low-season pricing floors** for March, September, and November because occupancy and margin are weaker.
3. **Prioritize 60+ day receivables** before normal statement follow-up because this bucket carries the highest collection risk.
4. **Monitor Rooms and Food & Beverage costs monthly** because these departments represent the largest cost share.
5. **Use revenue per labor hour** to compare staffing efficiency between peak and off-peak months.

---

## Dataset

The dataset is simulated with Python and modeled on realistic hotel operations over a 12-month period. It is designed to resemble data exported from ERP, property-management, finance, and operations systems.

| Table | Rows | Description | Example Business Use |
| --- | ---: | --- | --- |
| `bookings` | 14,605 | Room reservations with dates, room type, customer segment, and rate | Occupancy, ADR, seasonality, room mix |
| `invoices` | 14,605 | Customer billing records linked to bookings | Revenue recognition, invoice amounts, payment terms |
| `accounts_receivable` | 14,605 | Payment status and outstanding balances per invoice | AR aging, overdue risk, collection priority |
| `department_expenses` | 72 | Monthly cost records by department | Department cost control and profit margin analysis |
| `employee_shifts` | 2,190 | Staff scheduling and labor hours by department | Labor planning and staffing efficiency |
| `daily_sales` | 1,825 | Revenue by category per day | Revenue mix and dashboard visuals |

---

## KPIs Tracked

| KPI | Formula / Logic | Business Value |
| --- | --- | --- |
| Occupancy Rate % | Occupied room nights ÷ available room nights | Measures utilization and seasonal demand |
| ADR | Room revenue ÷ occupied room nights | Tracks pricing performance |
| Revenue by Category | Sum of daily sales by category | Shows which services drive revenue |
| Cost by Department | Sum of monthly department expenses | Identifies cost-heavy departments |
| AR Aging | Outstanding balances grouped into Paid, 0-30, 31-60, and 60+ days | Prioritizes collection action |
| Monthly Profit Margin % | Operating profit ÷ revenue | Measures monthly financial performance |
| Outstanding Receivables | Sum of unpaid invoice balances | Quantifies cash collection exposure |
| Labor Hours | Scheduled hours by department and date | Supports staffing and productivity analysis |
| Revenue per Labor Hour | Revenue ÷ labor hours | Measures staffing productivity |

---

## Project Structure

```text
operational-performance-analytics/
├── analysis/
│   ├── generate_results.py            # Creates final KPI outputs and dashboard preview
│   ├── hotel_analysis.ipynb           # Notebook starter for exploratory analysis
│   └── outputs/                       # Completed KPI exports and written findings
├── dashboard/
│   ├── executive_dashboard.html       # Static dashboard preview for GitHub reviewers
│   ├── power_bi_measures.md           # DAX measures for a Power BI version
│   └── README.md                      # Dashboard build notes
├── data/
│   ├── generate_data.py               # Repeatable simulated data generator
│   ├── load_to_postgres.py            # Optional PostgreSQL CSV loader
│   └── raw/                           # Generated completed dataset
├── docs/
│   └── data_model.md                  # Data model and table-grain documentation
├── screenshots/
│   └── README.md                      # Screenshot export guidance
├── sql/
│   ├── ar_aging.sql                   # Accounts receivable aging queries
│   ├── kpi_queries.sql                # KPI validation queries
│   ├── schema.sql                     # PostgreSQL tables, constraints, and indexes
│   └── views.sql                      # Analytical views for Power BI
├── LICENSE
├── README.md
└── requirements.txt
```

---

## How to Reproduce the Project

### 1. Create and activate a Python environment

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows PowerShell
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Regenerate the simulated dataset

The data generator uses only the Python standard library.

```bash
python data/generate_data.py --output-dir data/raw
```

### 4. Recreate KPI outputs and dashboard preview

```bash
python analysis/generate_results.py
```

This command writes the final CSV summaries in `analysis/outputs/` and refreshes `dashboard/executive_dashboard.html`.

### 5. Optional: create PostgreSQL tables

```bash
createdb hotel_operations
psql -d hotel_operations -f sql/schema.sql
```

### 6. Optional: load generated CSV data into PostgreSQL

```bash
python data/load_to_postgres.py --database-url postgresql://user:password@localhost:5432/hotel_operations
```

### 7. Optional: create analytical views and run SQL checks

```bash
psql -d hotel_operations -f sql/views.sql
psql -d hotel_operations -f sql/kpi_queries.sql
psql -d hotel_operations -f sql/ar_aging.sql
```

---

## Power BI Dashboard Plan

The project is Power BI-ready. Import the SQL views from `sql/views.sql` or import the CSV outputs directly.

Recommended report pages:

1. **Executive Overview** — revenue, cost, margin, occupancy, ADR, and outstanding receivables.
2. **Operations Performance** — occupancy trend, labor hours, revenue per labor hour, room type mix.
3. **Finance and P&L** — revenue, department expenses, operating profit, and profit margin trend.
4. **Accounts Receivable** — aging buckets, overdue customer drill-through, and outstanding balance details.

A static HTML preview is included at `dashboard/executive_dashboard.html` for reviewers who do not have Power BI installed.

---

## Business Value

This project demonstrates how ERP-style operational data can be converted into management insight. It supports:

- Better seasonal staffing and purchasing decisions.
- Faster identification of overdue customer balances.
- Clearer monthly revenue, cost, and margin review.
- Stronger discussion of operational KPIs in accounting, ERP, SAP, or business analyst interviews.
- A complete GitHub portfolio project with reproducible data, SQL, analysis outputs, and dashboard documentation.

---

## Skills Demonstrated

- Relational database design and ERP-aligned table modeling.
- PostgreSQL schema creation, constraints, indexes, analytical views, and KPI queries.
- SQL joins, aggregations, `CASE WHEN`, window functions, and dashboard-ready views.
- Python data generation and repeatable KPI export automation.
- Financial analytics: P&L, AR aging, margin, department costs, and collection risk.
- Business Intelligence dashboard planning with Power BI-ready DAX measures.
- Portfolio-ready documentation for ERP, SAP, accounting analytics, and business analytics roles.

---

## Suggested Resume Bullet

> Built an end-to-end hotel operations analytics project using Python, PostgreSQL, SQL, and Power BI-ready outputs; modeled ERP-style bookings, invoices, accounts receivable, department expenses, labor schedules, and daily sales to analyze occupancy, ADR, profit margin, revenue mix, labor productivity, and AR aging risk.
