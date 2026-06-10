-- PostgreSQL schema for the Hotel Operations Performance Analytics Dashboard.
-- Amount fields are stored in Japanese yen (JPY) to match the author's hotel context.

CREATE TABLE IF NOT EXISTS bookings (
    booking_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    customer_segment VARCHAR(50) NOT NULL,
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    room_type VARCHAR(50) NOT NULL,
    rooms_booked INTEGER NOT NULL CHECK (rooms_booked > 0),
    room_rate_jpy NUMERIC(12, 2) NOT NULL CHECK (room_rate_jpy >= 0),
    CHECK (check_out_date > check_in_date)
);

CREATE TABLE IF NOT EXISTS invoices (
    invoice_id INTEGER PRIMARY KEY,
    booking_id INTEGER NOT NULL REFERENCES bookings(booking_id),
    customer_id INTEGER NOT NULL,
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    payment_terms_days INTEGER NOT NULL CHECK (payment_terms_days > 0),
    room_revenue_jpy NUMERIC(14, 2) NOT NULL CHECK (room_revenue_jpy >= 0),
    ancillary_revenue_jpy NUMERIC(14, 2) NOT NULL CHECK (ancillary_revenue_jpy >= 0),
    invoice_amount_jpy NUMERIC(14, 2) NOT NULL CHECK (invoice_amount_jpy >= 0),
    CHECK (due_date >= invoice_date)
);

CREATE TABLE IF NOT EXISTS accounts_receivable (
    ar_id INTEGER PRIMARY KEY,
    invoice_id INTEGER NOT NULL REFERENCES invoices(invoice_id),
    customer_id INTEGER NOT NULL,
    payment_date DATE,
    amount_paid_jpy NUMERIC(14, 2) NOT NULL CHECK (amount_paid_jpy >= 0),
    outstanding_balance_jpy NUMERIC(14, 2) NOT NULL CHECK (outstanding_balance_jpy >= 0),
    days_past_due INTEGER NOT NULL CHECK (days_past_due >= 0),
    payment_status VARCHAR(20) NOT NULL CHECK (payment_status IN ('Open', 'Paid'))
);

CREATE TABLE IF NOT EXISTS department_expenses (
    expense_id INTEGER PRIMARY KEY,
    expense_month DATE NOT NULL,
    department VARCHAR(50) NOT NULL,
    expense_category VARCHAR(50) NOT NULL,
    amount_jpy NUMERIC(14, 2) NOT NULL CHECK (amount_jpy >= 0)
);

CREATE TABLE IF NOT EXISTS employee_shifts (
    shift_id INTEGER PRIMARY KEY,
    work_date DATE NOT NULL,
    department VARCHAR(50) NOT NULL,
    labor_hours NUMERIC(8, 2) NOT NULL CHECK (labor_hours >= 0),
    scheduled_staff INTEGER NOT NULL CHECK (scheduled_staff >= 0)
);

CREATE TABLE IF NOT EXISTS daily_sales (
    sales_id INTEGER PRIMARY KEY,
    sales_date DATE NOT NULL,
    revenue_category VARCHAR(50) NOT NULL,
    amount_jpy NUMERIC(14, 2) NOT NULL CHECK (amount_jpy >= 0)
);

CREATE INDEX IF NOT EXISTS idx_bookings_check_in_date ON bookings(check_in_date);
CREATE INDEX IF NOT EXISTS idx_invoices_invoice_date ON invoices(invoice_date);
CREATE INDEX IF NOT EXISTS idx_ar_customer_status ON accounts_receivable(customer_id, payment_status);
CREATE INDEX IF NOT EXISTS idx_daily_sales_date_category ON daily_sales(sales_date, revenue_category);
CREATE INDEX IF NOT EXISTS idx_department_expenses_month_department ON department_expenses(expense_month, department);
