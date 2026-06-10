# Data Model

The project follows an ERP-style analytical model for hotel operations. The tables are intentionally simple enough for portfolio review while still reflecting common finance, operations, and receivables reporting needs.

## Table Grain

| Table | Grain | Business Purpose |
| --- | --- | --- |
| `bookings` | One booking/stay record | Occupancy, room type, customer segment, and ADR analysis |
| `invoices` | One invoice per booking | Billing, room revenue, ancillary revenue, and payment terms |
| `accounts_receivable` | One AR record per invoice | Outstanding balance, payment status, and aging analysis |
| `department_expenses` | One department expense record per month | Department cost and profit margin analysis |
| `employee_shifts` | One department staffing record per day | Labor hours and staffing trend analysis |
| `daily_sales` | One revenue category per day | Revenue category mix and seasonal revenue trend analysis |

## Relationships

- `bookings.booking_id` → `invoices.booking_id`
- `invoices.invoice_id` → `accounts_receivable.invoice_id`
- `daily_sales.sales_date`, `department_expenses.expense_month`, and `employee_shifts.work_date` connect to a Power BI date table.

## Star Schema Interpretation

| Fact Area | Fact Table | Typical Dimensions |
| --- | --- | --- |
| Room operations | `bookings` | Date, room type, customer segment |
| Billing | `invoices` | Date, customer, booking |
| Collections | `accounts_receivable` | Customer, invoice, aging bucket |
| Cost control | `department_expenses` | Month, department, expense category |
| Labor planning | `employee_shifts` | Date, department |
| Revenue mix | `daily_sales` | Date, revenue category |

## Power BI Modeling Notes

- Create a separate Date table and relate it to `sales_date`, `check_in_date`, `invoice_date`, `expense_month`, and `work_date` as needed.
- Keep one active relationship to the Date table per visual context, or use DAX with inactive relationships if building a more advanced model.
- Use the SQL views in `sql/views.sql` when you want a clean semantic layer before Power BI.
- Use `analysis/outputs/*.csv` when you want a lightweight demo without a database connection.

## Data Quality Rules

| Rule | Reason |
| --- | --- |
| `check_out_date > check_in_date` | Prevents zero-night or negative-night stays |
| `invoice_amount_jpy >= 0` | Prevents invalid billing values |
| `outstanding_balance_jpy >= 0` | Prevents invalid receivables balances |
| `payment_status IN ('Open', 'Paid')` | Keeps AR status reporting consistent |
| `rooms_booked > 0` | Prevents impossible booking records |
