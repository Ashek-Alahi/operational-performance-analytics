# Data Model

The project follows a simple ERP-style analytical model for hotel operations.

| Table | Grain | Business Purpose |
| --- | --- | --- |
| `bookings` | One booking/stay record | Occupancy, room type, customer segment, and ADR analysis |
| `invoices` | One invoice per booking | Billing, room revenue, ancillary revenue, and payment terms |
| `accounts_receivable` | One AR record per invoice | Outstanding balance, payment status, and aging analysis |
| `department_expenses` | One department expense category per month | Department cost and profit margin analysis |
| `employee_shifts` | One department staffing record per day | Labor hours and staffing trend analysis |
| `daily_sales` | One revenue category per day | Revenue category mix and seasonal revenue trend analysis |

## Relationships

- `bookings.booking_id` → `invoices.booking_id`
- `invoices.invoice_id` → `accounts_receivable.invoice_id`
- `daily_sales.sales_date`, `department_expenses.expense_month`, and `employee_shifts.work_date` connect to a Power BI date table.
