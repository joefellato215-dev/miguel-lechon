from pathlib import Path
import os
import sqlite3


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = Path(
    os.environ.get(
        "DATABASE_PATH",
        str(BASE_DIR / "miguel_lechon.db"),
    )
)
SCHEMA_PATH = BASE_DIR / "schema.sql"


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    conn = get_connection()
    try:
        conn.executescript(schema)
        conn.commit()
    finally:
        conn.close()


def create_order(
    customer_name,
    phone,
    event_date,
    preferred_order,
    notes,
    contact_method,
):
    conn = get_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO orders (
                customer_name,
                phone,
                event_date,
                preferred_order,
                notes,
                contact_method
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                customer_name,
                phone,
                event_date,
                preferred_order,
                notes,
                contact_method,
            ),
        )

        conn.commit()
        return cursor.lastrowid

    finally:
        conn.close()



def update_order_status(order_id, status):
    conn = get_connection()

    try:
        cursor = conn.execute(
            """
            UPDATE orders
            SET
                status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, order_id),
        )

        conn.commit()

        if cursor.rowcount == 0:
            return False

        return True
    finally:
        conn.close()

def list_orders():
    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                id,
                customer_name,
                phone,
                event_date,
                preferred_order,
                notes,
                contact_method,
                status,
                created_at,
                updated_at
            FROM orders
            ORDER BY id DESC
            """
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()
