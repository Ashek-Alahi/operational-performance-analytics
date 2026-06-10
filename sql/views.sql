-- Analytical views designed for Power BI import or DirectQuery.

CREATE OR REPLACE VIEW vw_monthly_occupancy AS
WITH room_nights AS (
    SELECT
        date_trunc('month', check_in_date)::date AS month,
        SUM((check_out_date - check_in_date) * rooms_booked) AS occupied_room_nights
    FROM bookings
    GROUP BY 1
)
SELECT
    month,
    occupied_room_nights,
    120 * EXTRACT(day FROM (month + INTERVAL '1 month - 1 day')) AS available_room_nights,
    ROUND(
        occupied_room_nights / NULLIF(120 * EXTRACT(day FROM (month + INTERVAL '1 month - 1 day')), 0) * 100,
        2
    ) AS occupancy_rate_pct
FROM room_nights;

CREATE OR REPLACE VIEW vw_monthly_adr AS
SELECT
    date_trunc('month', b.check_in_date)::date AS month,
    SUM(i.room_revenue_jpy) AS room_revenue_jpy,
    SUM((b.check_out_date - b.check_in_date) * b.rooms_booked) AS occupied_room_nights,
    ROUND(
        SUM(i.room_revenue_jpy)
        / NULLIF(SUM((b.check_out_date - b.check_in_date) * b.rooms_booked), 0),
        2
    ) AS adr_jpy
FROM invoices i
JOIN bookings b ON b.booking_id = i.booking_id
GROUP BY 1;

CREATE OR REPLACE VIEW vw_monthly_profit_margin AS
WITH monthly_revenue AS (
    SELECT
        date_trunc('month', sales_date)::date AS month,
        SUM(amount_jpy) AS revenue_jpy
    FROM daily_sales
    GROUP BY 1
), monthly_cost AS (
    SELECT
        expense_month AS month,
        SUM(amount_jpy) AS operating_cost_jpy
    FROM department_expenses
    GROUP BY 1
)
SELECT
    r.month,
    r.revenue_jpy,
    COALESCE(c.operating_cost_jpy, 0) AS operating_cost_jpy,
    r.revenue_jpy - COALESCE(c.operating_cost_jpy, 0) AS operating_profit_jpy,
    ROUND((r.revenue_jpy - COALESCE(c.operating_cost_jpy, 0)) / NULLIF(r.revenue_jpy, 0) * 100, 2) AS profit_margin_pct
FROM monthly_revenue r
LEFT JOIN monthly_cost c ON c.month = r.month;

CREATE OR REPLACE VIEW vw_monthly_labor_productivity AS
WITH monthly_revenue AS (
    SELECT
        date_trunc('month', sales_date)::date AS month,
        SUM(amount_jpy) AS revenue_jpy
    FROM daily_sales
    GROUP BY 1
), monthly_labor AS (
    SELECT
        date_trunc('month', work_date)::date AS month,
        SUM(labor_hours) AS labor_hours,
        SUM(scheduled_staff) AS scheduled_staff_shifts
    FROM employee_shifts
    GROUP BY 1
)
SELECT
    r.month,
    r.revenue_jpy,
    l.labor_hours,
    l.scheduled_staff_shifts,
    ROUND(r.revenue_jpy / NULLIF(l.labor_hours, 0), 2) AS revenue_per_labor_hour_jpy
FROM monthly_revenue r
JOIN monthly_labor l ON l.month = r.month;

CREATE OR REPLACE VIEW vw_ar_aging AS
SELECT
    ar.customer_id,
    ar.invoice_id,
    i.invoice_date,
    i.due_date,
    ar.payment_status,
    ar.outstanding_balance_jpy,
    ar.days_past_due,
    CASE
        WHEN ar.outstanding_balance_jpy = 0 THEN 'Paid'
        WHEN ar.days_past_due BETWEEN 0 AND 30 THEN '0-30 days'
        WHEN ar.days_past_due BETWEEN 31 AND 60 THEN '31-60 days'
        ELSE '60+ days'
    END AS aging_bucket
FROM accounts_receivable ar
JOIN invoices i ON i.invoice_id = ar.invoice_id;

CREATE OR REPLACE VIEW vw_ar_aging_summary AS
SELECT
    aging_bucket,
    COUNT(*) AS invoice_count,
    COUNT(DISTINCT customer_id) AS customer_count,
    SUM(outstanding_balance_jpy) AS outstanding_balance_jpy
FROM vw_ar_aging
GROUP BY aging_bucket;

CREATE OR REPLACE VIEW vw_revenue_category_monthly AS
SELECT
    date_trunc('month', sales_date)::date AS month,
    revenue_category,
    SUM(amount_jpy) AS revenue_jpy,
    ROUND(
        SUM(amount_jpy)
        / NULLIF(SUM(SUM(amount_jpy)) OVER (PARTITION BY date_trunc('month', sales_date)), 0) * 100,
        2
    ) AS category_share_pct
FROM daily_sales
GROUP BY 1, 2;

CREATE OR REPLACE VIEW vw_executive_monthly_kpis AS
SELECT
    p.month,
    p.revenue_jpy,
    p.operating_cost_jpy,
    p.operating_profit_jpy,
    p.profit_margin_pct,
    o.occupied_room_nights,
    o.available_room_nights,
    o.occupancy_rate_pct,
    a.adr_jpy,
    l.labor_hours,
    l.revenue_per_labor_hour_jpy
FROM vw_monthly_profit_margin p
LEFT JOIN vw_monthly_occupancy o ON o.month = p.month
LEFT JOIN vw_monthly_adr a ON a.month = p.month
LEFT JOIN vw_monthly_labor_productivity l ON l.month = p.month;
