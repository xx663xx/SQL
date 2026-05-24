import os
import sqlite3

from .config import DB_PATH, SCHEMA_PATH, SEED_PATH


def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn):
    with open(SCHEMA_PATH, "r", encoding="utf-8") as file:
        conn.executescript(file.read())

    car_columns = {row[1] for row in conn.execute("PRAGMA table_info(cars)")}
    if "mileage" not in car_columns:
        conn.execute("ALTER TABLE cars ADD COLUMN mileage INTEGER NOT NULL DEFAULT 0 CHECK (mileage >= 0)")
        conn.execute(
            """
            UPDATE cars
            SET mileage = CASE car_id
                WHEN 1 THEN 18000
                WHEN 2 THEN 42000
                WHEN 3 THEN 61000
                WHEN 4 THEN 35000
                WHEN 5 THEN 58000
                WHEN 6 THEN 12000
                WHEN 7 THEN 76000
                WHEN 8 THEN 39000
                WHEN 9 THEN 54000
                WHEN 10 THEN 15000
                WHEN 11 THEN 82000
                WHEN 12 THEN 47000
                WHEN 13 THEN 33000
                WHEN 14 THEN 52000
                WHEN 15 THEN 69000
                WHEN 16 THEN 64000
                WHEN 17 THEN 27000
                WHEN 18 THEN 88000
                WHEN 19 THEN 9000
                WHEN 20 THEN 31000
                ELSE mileage
            END
            """
        )

    sales_columns = {row[1] for row in conn.execute("PRAGMA table_info(sales)")}
    sales_migrations = [
        ("contract_number", "ALTER TABLE sales ADD COLUMN contract_number TEXT"),
        (
            "payment_status",
            "ALTER TABLE sales ADD COLUMN payment_status TEXT NOT NULL DEFAULT 'оплачено'",
        ),
        ("payment_method", "ALTER TABLE sales ADD COLUMN payment_method TEXT"),
        ("payment_date", "ALTER TABLE sales ADD COLUMN payment_date TEXT"),
        ("contract_file", "ALTER TABLE sales ADD COLUMN contract_file TEXT"),
    ]
    for column_name, alter_sql in sales_migrations:
        if column_name not in sales_columns:
            conn.execute(alter_sql)

    conn.execute(
        """
        UPDATE sales
        SET contract_number = printf('ДП-%04d', sale_id)
        WHERE contract_number IS NULL OR contract_number = ''
        """
    )
    conn.execute(
        """
        UPDATE sales
        SET payment_method = 'банк',
            payment_date = sale_date
        WHERE payment_status = 'оплачено'
          AND (payment_method IS NULL OR payment_method = '' OR payment_date IS NULL OR payment_date = '')
        """
    )

    cars_count = conn.execute("SELECT COUNT(*) FROM cars").fetchone()[0]
    if cars_count == 0 and os.path.exists(SEED_PATH):
        with open(SEED_PATH, "r", encoding="utf-8") as file:
            conn.executescript(file.read())

    reservations_count = conn.execute("SELECT COUNT(*) FROM reservations").fetchone()[0]
    if reservations_count == 0 and conn.execute("SELECT COUNT(*) FROM cars").fetchone()[0] > 0:
        conn.executemany(
            """
            INSERT INTO reservations
                (reservation_id, car_id, client_id, employee_id, reservation_date, valid_until, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (1, 16, 3, 12, "2026-03-03", "2026-03-10", "активна"),
                (2, 17, 4, 1, "2026-03-12", "2026-03-19", "активна"),
                (3, 18, 5, 2, "2026-03-18", "2026-03-25", "активна"),
            ],
        )
    conn.commit()
