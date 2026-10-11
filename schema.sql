-- Table structure (PostgreSQL/MySQL/SQLite compatible, minor type changes ho sakte hain)
-- Note: 01_cleaning.py pandas se tables auto-create karta hai; yeh file documentation
-- aur MySQL/PostgreSQL mein manually load karne ke liye hai.

CREATE TABLE customers (
    customer_id  VARCHAR(10) PRIMARY KEY,
    city         VARCHAR(50),
    state        VARCHAR(50),
    signup_date  DATE
);

CREATE TABLE products (
    product_id   VARCHAR(10) PRIMARY KEY,
    category     VARCHAR(50),
    price        DECIMAL(10,2)
);

CREATE TABLE orders (
    order_id                 VARCHAR(10) PRIMARY KEY,
    customer_id              VARCHAR(10) REFERENCES customers(customer_id),
    order_date               DATE,
    estimated_delivery_date  DATE,
    delivered_date           DATE,
    order_status             VARCHAR(20),
    review_rating            INT,
    delivery_days            INT,
    delay_days               INT,
    is_late                  INT
);

CREATE TABLE order_items (
    order_id     VARCHAR(10) REFERENCES orders(order_id),
    product_id   VARCHAR(10) REFERENCES products(product_id),
    quantity     INT,
    unit_price   DECIMAL(10,2),
    discount     DECIMAL(4,2),
    revenue      DECIMAL(12,2)
);

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date     ON orders(order_date);
CREATE INDEX idx_items_order     ON order_items(order_id);
CREATE INDEX idx_items_product   ON order_items(product_id);
