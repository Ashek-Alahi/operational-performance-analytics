# Interview Positioning Guide

## What This Project Proves

- You can model operational and financial business processes in structured data.
- You can generate reproducible datasets and validate outputs.
- You understand hotel-style KPIs: occupancy, ADR, revenue mix, department cost, profit margin, labor productivity, and AR aging.
- You can connect accounting/ERP concepts to SQL, Python, and dashboard-ready reporting.

## What This Project Does Not Prove

- It is not a real hotel implementation.
- It is not a real SAP S/4HANA implementation.
- It does not use real company data.
- It is not a production forecasting system.
- It does not include a finished Power BI `.pbix` file unless one is added later.

## ERP/SAP Relevance

The project is ERP-relevant because it resembles common ERP reporting flows: operational activity creates billing, billing creates receivables, departments incur costs, labor supports operations, and management reviews KPIs. You can connect the discussion to SAP FI/CO-style concepts such as receivables, cost centers, revenue, profitability, and management reporting.

Use careful language: “ERP-style” or “SAP-relevant analytics,” not “SAP implementation.”

## Business Analytics Relevance

The project turns transactional-style data into management outputs: KPI tables, AR aging, revenue category summaries, department cost summaries, customer collection priorities, and a static executive dashboard preview.

## Limitations

- Simulated dataset.
- One-year period only.
- No external market/weather/event variables.
- Not a live ERP connection.
- Not a production forecasting system.
- Not an actual SAP implementation.
- Power BI-ready, but not a full PBIX dashboard unless a PBIX file is added.

## 30-Second Explanation

“I built a simulated ERP-style hotel operations analytics project. It generates hotel operations, billing, AR, expense, labor, and sales data, then uses Python and SQL logic to calculate KPIs like occupancy, ADR, profit margin, revenue mix, labor productivity, and receivables aging. The outputs are reproducible CSVs, SQL views, a static HTML dashboard preview, and Power BI-ready measures.”

## 1-Minute Explanation

“This project is a portfolio analytics dashboard for hotel operations. I created deterministic simulated data for bookings, invoices, accounts receivable, department expenses, employee shifts, and daily sales. Then I built Python scripts to generate monthly KPIs, revenue category summaries, department cost summaries, AR aging, customer collection priorities, an executive Markdown summary, and a static dashboard preview. I also included PostgreSQL schema and view SQL so the same model can be reviewed from a database perspective. The purpose is to demonstrate ERP-style analytics and management reporting, not to claim a real hotel or SAP implementation.”

## 3-Minute Explanation

“The business problem is that hospitality managers often review operations, finance, labor, and AR in separate reports. I modeled those areas in a simulated ERP-style dataset. Bookings create occupancy and ADR metrics; invoices represent billing; accounts receivable supports aging and collection-risk reporting; department expenses support cost and margin analysis; employee shifts support labor productivity; and daily sales supports revenue mix. The Python pipeline regenerates the data with a fixed seed, produces KPI outputs, validates required files and business rules, and refreshes the static HTML dashboard. SQL files provide a PostgreSQL schema, analytical views, and KPI checks. In interviews, I position this as evidence that I understand accounting, ERP data flows, SQL/Python analytics, and management reporting. I am careful to say it is simulated and ERP-style, not real SAP or production client work.”

## Likely Interview Questions

| Question | Short Answer |
| --- | --- |
| Is this real hotel data? | No. It is simulated data designed to resemble ERP/PMS/finance exports. |
| Is this an SAP project? | No. It is SAP/ERP-relevant analytics, but not an SAP implementation. |
| Why use simulated data? | It avoids confidentiality issues and makes the project reproducible for reviewers. |
| What business question does it answer? | It shows which months, revenue categories, departments, labor patterns, and AR buckets need management attention. |
| What would you improve next? | Add a PBIX file, dimensional date table, richer external drivers, and more formal data-quality tests. |
