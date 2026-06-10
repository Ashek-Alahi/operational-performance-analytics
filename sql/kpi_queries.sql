-- Core KPI queries for hotel operations analysis.

-- 1. Monthly occupancy rate based on occupied room nights.
WITH room_nights AS (
    SELECT
        date_trunc('month', check_in_date)::date AS month,
        SUM((check_out_date - check_in_date) * rooms_booked) AS occupied_room_nights
    FROM bookings
    GROUP BY 1
), month_capacity AS (
    SELECT
        month,
        occupied_room_nights,
        120 * EXTRACT(day FROM (month + INTERVAL '1 month - 1 day')) AS available_room_nights
    FROM room_nights
)
SELECT
    month,
    occupied_room_nights,
    available_room_nights,
    ROUND(occupied_room_nights / NULLIF(available_room_nights, 0) * 100, 2) AS occupancy_rate_pct
FROM month_capacity
ORDER BY month;

-- 2. Average daily rate (ADR) by month.
SELECT
    date_trunc('month', b.check_in_date)::date AS month,
    ROUND(SUM(i.room_revenue_jpy) / NULLIF(SUM(b.rooms_booked * (b.check_out_date - b.check_in_date)), 0), 2) AS adr_jpy
FROM invoices i
JOIN bookings b ON b.booking_id = i.booking_id
GROUP BY 1
ORDER BY 1;

-- 3. Revenue by category and monthly contribution percentage.
SELECT
    date_trunc('month', sales_date)::date AS month,
    revenue_category,
    SUM(amount_jpy) AS revenue_jpy,
    ROUND(
        SUM(amount_jpy) / NULLIF(SUM(SUM(amount_jpy)) OVER (PARTITION BY date_trunc('month', sales_date)), 0) * 100,
        2
    ) AS category_share_pct
FROM daily_sales
GROUP BY 1, 2
ORDER BY 1, revenue_jpy DESC;

-- 4. Cost by department with month-over-month variance.
WITH monthly_cost AS (
    SELECT
        expense_month AS month,
        department,
        SUM(amount_jpy) AS cost_jpy
    FROM department_expenses
    GROUP BY 1, 2
)
SELECT
    month,
    department,
    cost_jpy,
    cost_jpy - LAG(cost_jpy) OVER (PARTITION BY department ORDER BY month) AS cost_change_jpy,
    ROUND(
        (cost_jpy - LAG(cost_jpy) OVER (PARTITION BY department ORDER BY month))
        / NULLIF(LAG(cost_jpy) OVER (PARTITION BY department ORDER BY month), 0) * 100,
        2
    ) AS cost_change_pct
FROM monthly_cost
ORDER BY month, department;

-- 5. Executive monthly KPI dataset for dashboard validation.
SELECT
    month,
    revenue_jpy,
    operating_cost_jpy,
    operating_profit_jpy,
    profit_margin_pct,
    occupied_room_nights,
    available_room_nights,
    occupancy_rate_pct,
    adr_jpy,
    labor_hours,
    revenue_per_labor_hour_jpy
FROM vw_executive_monthly_kpis
ORDER BY month;
