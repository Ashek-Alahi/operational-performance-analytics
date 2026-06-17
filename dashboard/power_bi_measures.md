# Power BI-Ready Measures and Dashboard Design Plan

Use these DAX measures after importing the PostgreSQL views or generated CSV files. They are written for accounting and ERP-style KPI validation.

> This repository does not include a completed `.pbix` file. These are Power BI-ready measures and design notes.

```DAX
Total Revenue JPY = SUM('vw_monthly_profit_margin'[revenue_jpy])

Operating Cost JPY = SUM('vw_monthly_profit_margin'[operating_cost_jpy])

Operating Profit JPY = [Total Revenue JPY] - [Operating Cost JPY]

Profit Margin % = DIVIDE([Operating Profit JPY], [Total Revenue JPY])

Occupied Room Nights = SUM('vw_monthly_occupancy'[occupied_room_nights])

Available Room Nights = SUM('vw_monthly_occupancy'[available_room_nights])

Occupancy Rate % = DIVIDE([Occupied Room Nights], [Available Room Nights])

ADR JPY = AVERAGE('vw_monthly_adr'[adr_jpy])

Outstanding AR JPY = SUM('vw_ar_aging'[outstanding_balance_jpy])

Overdue AR JPY =
CALCULATE(
    [Outstanding AR JPY],
    'vw_ar_aging'[aging_bucket] IN {"0-30 days", "31-60 days", "60+ days"}
)

60+ Day AR JPY =
CALCULATE(
    [Outstanding AR JPY],
    'vw_ar_aging'[aging_bucket] = "60+ days"
)
```

## Recommended Visuals

| Page | Visual | Business Question |
| --- | --- | --- |
| Executive Overview | KPI cards for revenue, margin, occupancy, ADR, and AR | Is the hotel financially healthy this year? |
| Operations | Monthly occupancy and labor-hours trend | Are staffing levels aligned with demand? |
| Finance | Revenue, cost, and profit-margin combo chart | Which months drive profitability? |
| Accounts Receivable | Aging bucket bar chart and customer table | Which balances need collection action first? |
