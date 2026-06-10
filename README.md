# Hotel Operations Performance Analytics Dashboard

![Project Status](https://img.shields.io/badge/status-in%20progress-yellow)
![Tools](https://img.shields.io/badge/tools-Python%20%7C%20PostgreSQL%20%7C%20Power%20BI-blue)
![Domain](https://img.shields.io/badge/domain-Hospitality%20Analytics-green)

**Tools:** Python · PostgreSQL · SQL · Power BI<br>
**Duration:** 4 weeks<br>
**Domain:** Hospitality · Operational Analytics · Financial Analytics<br>
**Business Context:** Hotel ERP-style operations, revenue, cost, labor, and accounts receivable analytics

---

## Business Problem

Hotel managers often lack a centralized view of operational and financial performance. Revenue may be reviewed separately from operating costs, accounts receivable aging is often monitored manually, and seasonal occupancy patterns may be identified too late to support staffing, pricing, and collection decisions.

This project builds an end-to-end analytics solution that consolidates hotel operations, finance, labor, and customer payment behavior into a single Power BI dashboard. The goal is to help management answer practical questions:

- Which revenue categories and departments create the most value?
- Which months show the strongest occupancy and profit margin?
- Which customers are creating collection risk through overdue balances?
- Are labor hours and department expenses aligned with seasonal demand?
- Where should management focus pricing, staffing, and cash collection actions?

---

## Objectives

- Identify the revenue categories and departments driving the most value.
- Track accounts receivable aging and flag chronic late-paying customers.
- Analyze occupancy trends, seasonal demand, and peak/off-peak periods.
- Calculate monthly profit margin, ADR, and operational KPIs.
- Create SQL views that can be imported into Power BI for reporting.
- Deliver a professional dashboard structure suitable for a GitHub portfolio and resume discussion.

---

## Dataset

The dataset is simulated with Python and modeled on realistic hotel operations over a 12-month period. It is designed to look like data exported from ERP, property-management, finance, and operations systems.

| Table | Description | Example Business Use |
| --- | --- | --- |
| `bookings` | Room reservations with check-in/check-out dates, room type, customer segment, and rate | Occupancy, ADR, seasonality, room mix |
| `invoices` | Customer billing records linked to bookings | Revenue recognition, invoice amounts, payment terms |
| `accounts_receivable` | Payment status and outstanding balances per invoice | AR aging, overdue risk, customer collection priority |
| `department_expenses` | Monthly cost records by department | Department cost control and profit margin analysis |
| `employee_shifts` | Staff scheduling and labor hours by department | Labor planning and staffing efficiency |
| `daily_sales` | Revenue by category per day | Revenue mix, category trends, dashboard visuals |

> The generated sample data uses Japanese yen (JPY) because the project is positioned around a Japan hotel/resort operations context.

---

## KPIs Tracked

| KPI | Formula / Logic | Business Value |
| --- | --- | --- |
| Occupancy Rate % | Occupied room nights ÷ available room nights | Measures room utilization and seasonal demand |
| ADR | Room revenue ÷ occupied room nights | Tracks pricing performance |
| Revenue by Category | Sum of daily sales by category | Shows which services drive revenue |
| Cost by Department | Sum of monthly department expenses | Identifies cost-heavy departments |
| AR Aging | Outstanding balances grouped into 0-30, 31-60, and 60+ days | Prioritizes collection action |
| Monthly Profit Margin % | Operating profit ÷ revenue | Measures monthly financial performance |
| Outstanding Receivables | Sum of unpaid invoice balances | Quantifies cash collection exposure |
| Labor Hours | Scheduled hours by department and date | Supports staffing and productivity analysis |

---

## Methodology

### Step 1 — Schema Design and Data Generation

Designed a relational schema with primary keys, foreign keys, date fields, and finance-oriented numeric fields. The Python data generator creates 12 months of simulated hotel operations data with seasonality, room type mix, payment delays, and department cost variation.

### Step 2 — SQL Analytics Layer

Built analytical SQL assets for PostgreSQL, including:

- `CASE WHEN` logic for AR aging buckets.
- Window functions such as `LAG()` and `PARTITION BY` for cost trend analysis.
- Monthly KPI queries for occupancy, ADR, revenue, and cost.
- Reusable SQL views for Power BI reporting.

### Step 3 — Python Analysis

Prepared a starter Jupyter notebook for Pandas-based validation and business analysis. The notebook is intended to calculate rolling averages, peak/off-peak season flags, AR concentration, and profit margin findings after the data is generated.

### Step 4 — Power BI Dashboard

Planned a four-page dashboard structure:

1. **Executive Overview** — KPI cards for revenue, cost, margin, occupancy, ADR, and outstanding receivables.
2. **Operations Performance** — occupancy trends, room type mix, department filters, and labor hours.
3. **Finance and P&L** — revenue, department expenses, operating profit, and profit margin trend.
4. **Accounts Receivable** — aging buckets, overdue customer drill-through, and outstanding balance details.

---

## Key Findings

This section should be updated after generating the data, loading it into PostgreSQL, and building the final dashboard. Replace the placeholders below with real numbers from the SQL views or Power BI report.

- Peak occupancy occurred in **[Month]**, with an average occupancy rate of **X%**.
- The **[Revenue Category]** category contributed the highest revenue at **X%** of total revenue.
- **X customers** carried receivables overdue by 60+ days, representing **¥X** in outstanding balance.
- Profit margin peaked in **[Month]** and declined in **[Month]**, mainly driven by **[cost factor]**.
- Department expenses were highest in **[Department]**, indicating a possible cost-control or staffing review area.

> Practical portfolio note: recruiters and hiring managers often look at this section first. Filling it with real numbers makes the project look like completed analytical work rather than a template.

---

## Repository Structure

```text
hotel-operations-analytics/
├── analysis/
│   └── hotel_analysis.ipynb          # Pandas analysis and trend calculations
├── dashboard/
│   └── README.md                     # Power BI dashboard build notes
├── data/
│   └── generate_data.py              # Simulated dataset generation script
├── docs/
│   └── data_model.md                 # Data model and table-grain documentation
├── screenshots/
│   └── README.md                     # Placeholder for exported dashboard images
├── sql/
│   ├── ar_aging.sql                  # Accounts receivable aging buckets
│   ├── kpi_queries.sql               # Occupancy, ADR, revenue, and cost queries
│   ├── schema.sql                    # Table definitions, constraints, and indexes
│   └── views.sql                     # Analytical SQL views for Power BI
├── LICENSE
├── README.md
└── requirements.txt
```

Generated CSV files are written to `data/raw/` by default. The folder is intentionally not committed so the repository can stay lightweight.

---

## How to Run This Project

### 1. Clone the repository

```bash
git clone <repository-url>
cd hotel-operations-analytics
```

### 2. Create and activate a Python environment

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows PowerShell
```

### 3. Generate simulated data

The data generator uses only the Python standard library, so it can be run before installing the analysis dependencies.

```bash
python data/generate_data.py --output-dir data/raw
```

### 4. Install analysis dependencies

Install these before running the Jupyter notebook or building a Python-based database load script.

```bash
pip install -r requirements.txt
```

Expected CSV outputs:

- `data/raw/bookings.csv`
- `data/raw/invoices.csv`
- `data/raw/accounts_receivable.csv`
- `data/raw/department_expenses.csv`
- `data/raw/employee_shifts.csv`
- `data/raw/daily_sales.csv`

### 5. Create PostgreSQL tables

```bash
psql -d hotel_operations -f sql/schema.sql
```

Load the CSV files into the matching PostgreSQL tables using your preferred method, such as `COPY`, pgAdmin import, or a Python loading script.

### 6. Run KPI queries and create views

```bash
psql -d hotel_operations -f sql/kpi_queries.sql
psql -d hotel_operations -f sql/ar_aging.sql
psql -d hotel_operations -f sql/views.sql
```

### 7. Build the Power BI dashboard

Connect Power BI to PostgreSQL and import the reporting views:

- `vw_monthly_occupancy`
- `vw_monthly_profit_margin`
- `vw_ar_aging`
- `vw_revenue_category_monthly`

---

## Dashboard Preview

Dashboard screenshots will be added after the Power BI report is completed.

Suggested screenshots:

| Page | Screenshot File |
| --- | --- |
| Executive Overview | `screenshots/executive-overview.png` |
| Operations Performance | `screenshots/operations-performance.png` |
| Finance and P&L | `screenshots/finance-profit-margin.png` |
| Accounts Receivable Aging | `screenshots/accounts-receivable-aging.png` |

---

## Business Value

This project demonstrates how an accountant or ERP analyst can move beyond transaction reporting and create management-level insight. The dashboard connects operational activity with financial outcomes, which supports:

- Better seasonal staffing and cost planning.
- Faster identification of overdue customer balances.
- Improved revenue category monitoring.
- Clearer monthly profit margin analysis.
- More informed pricing and department-performance discussions.

---

## Skills Demonstrated

- Relational database design and ERP-aligned table modeling.
- PostgreSQL schema creation, constraints, indexes, and analytical views.
- SQL joins, aggregations, `CASE WHEN`, window functions, and KPI logic.
- Python data generation using Pandas and NumPy.
- Financial analytics, including P&L, AR aging, margin, and cost analysis.
- Business Intelligence dashboard planning with Power BI.
- Portfolio-ready documentation for analytics and ERP career positioning.

---

## Recommended Next Improvements

- Add a Python CSV-to-PostgreSQL loading script.
- Add a date dimension table for Power BI time intelligence.
- Complete the Power BI `.pbix` file and export dashboard screenshots.
- Replace the Key Findings placeholders with final calculated values.
- Add DAX measures for occupancy, ADR, profit margin, and AR aging.
- Add a data quality checklist for missing dates, duplicate invoices, and negative balances.

---

## Author

**Ashek Alahi**<br>
Accountant · ERP Enthusiast · Analytics Learner<br>
Aomori Resort Co. Ltd., Japan<br>

- LinkedIn: `[Add LinkedIn URL]`
- Email: `[Add professional email]`

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
