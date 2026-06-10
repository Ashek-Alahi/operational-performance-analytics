-- Accounts receivable aging analysis.

WITH ar_bucketed AS (
    SELECT
        ar.customer_id,
        ar.invoice_id,
        i.due_date,
        ar.outstanding_balance_jpy,
        ar.days_past_due,
        CASE
            WHEN ar.outstanding_balance_jpy = 0 THEN 'Paid'
            WHEN ar.days_past_due BETWEEN 0 AND 30 THEN '0-30 days'
            WHEN ar.days_past_due BETWEEN 31 AND 60 THEN '31-60 days'
            ELSE '60+ days'
        END AS aging_bucket
    FROM accounts_receivable ar
    JOIN invoices i ON i.invoice_id = ar.invoice_id
)
SELECT
    aging_bucket,
    COUNT(*) AS invoice_count,
    COUNT(DISTINCT customer_id) AS customer_count,
    SUM(outstanding_balance_jpy) AS outstanding_balance_jpy
FROM ar_bucketed
GROUP BY aging_bucket
ORDER BY
    CASE aging_bucket
        WHEN 'Paid' THEN 1
        WHEN '0-30 days' THEN 2
        WHEN '31-60 days' THEN 3
        ELSE 4
    END;

-- Chronic late-paying customers for drill-through analysis.
SELECT
    customer_id,
    COUNT(*) FILTER (WHERE days_past_due > 60 AND outstanding_balance_jpy > 0) AS invoices_over_60_days,
    SUM(outstanding_balance_jpy) AS total_outstanding_jpy,
    MAX(days_past_due) AS oldest_days_past_due
FROM accounts_receivable
GROUP BY customer_id
HAVING COUNT(*) FILTER (WHERE days_past_due > 60 AND outstanding_balance_jpy > 0) > 0
ORDER BY total_outstanding_jpy DESC;
