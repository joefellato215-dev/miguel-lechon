CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    customer_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    event_date TEXT,
    preferred_order TEXT,
    notes TEXT,
    contact_method TEXT NOT NULL DEFAULT 'messenger',

    status TEXT NOT NULL DEFAULT 'NEW',

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_orders_status
ON orders(status);

CREATE INDEX IF NOT EXISTS idx_orders_event_date
ON orders(event_date);

CREATE INDEX IF NOT EXISTS idx_orders_created_at
ON orders(created_at);
