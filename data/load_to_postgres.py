"""Load generated CSV files into PostgreSQL tables.

Usage example:
    python data/load_to_postgres.py --database-url postgresql://user:password@localhost:5432/hotel_operations

Run ``psql -d hotel_operations -f sql/schema.sql`` before this loader so the
tables, constraints, and indexes already exist.
"""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path

from sqlalchemy import create_engine, text

LOAD_ORDER = [
    "bookings",
    "invoices",
    "accounts_receivable",
    "department_expenses",
    "employee_shifts",
    "daily_sales",
]


def load_table(engine, data_dir: Path, table_name: str) -> int:
    """Replace one PostgreSQL table with the matching generated CSV."""
    path = data_dir / f"{table_name}.csv"
    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)

    if not rows:
        raise ValueError(f"No rows found in {path}")

    with engine.begin() as connection:
        connection.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE"))
        connection.execute(text(f"INSERT INTO {table_name} ({', '.join(rows[0])}) VALUES ({', '.join(':' + key for key in rows[0])})"), rows)
    return len(rows)


def parse_args() -> argparse.Namespace:
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description="Load generated hotel CSV files into PostgreSQL.")
    parser.add_argument("--data-dir", type=Path, default=Path("data/raw"), help="Directory containing generated CSV files.")
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL"),
        help="SQLAlchemy PostgreSQL URL. Defaults to the DATABASE_URL environment variable.",
    )
    return parser.parse_args()


def main() -> None:
    """Load all generated CSV files in foreign-key-safe order."""
    args = parse_args()
    if not args.database_url:
        raise SystemExit("Provide --database-url or set the DATABASE_URL environment variable.")

    engine = create_engine(args.database_url)
    for table_name in LOAD_ORDER:
        row_count = load_table(engine, args.data_dir, table_name)
        print(f"Loaded {row_count:,} rows into {table_name}")


if __name__ == "__main__":
    main()
