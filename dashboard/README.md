# Dashboard Deliverables

This folder contains dashboard-ready assets for the Hotel Operations Performance Analytics project.

## Included Files

| File | Purpose |
| --- | --- |
| `executive_dashboard.html` | Static dashboard preview generated from `analysis/generate_results.py` for GitHub reviewers without Power BI |
| `power_bi_measures.md` | Recommended DAX measures for the Power BI version |

## Recommended Power BI Report Pages

1. **Executive Overview** — revenue, operating cost, profit margin, occupancy, ADR, and AR cards.
2. **Operations Performance** — monthly occupancy, labor hours, revenue per labor hour, and room type filters.
3. **Finance and P&L** — revenue, department costs, operating profit, and profit margin trend.
4. **Accounts Receivable** — aging buckets, customer collection priority, and overdue detail table.

## Data Sources

Use either option:

- PostgreSQL views from `../sql/views.sql`.
- CSV exports from `../analysis/outputs/` for a lightweight portfolio demo.

Export final Power BI page images to `../screenshots/` if you create a `.pbix` version locally.
