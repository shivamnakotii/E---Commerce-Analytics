-- =====================================================================
-- E-commerce Sales Analysis: SQL queries
-- Dialect: SQLite (PostgreSQL/MySQL ke liye date functions badalne honge,
-- jahan zaroori hai wahan comment mein diya hai)
-- Tables: customers, products, orders, order_items
-- =====================================================================

-- Q1. Headline KPIs (sirf delivered orders)
SELECT
    ROUND(SUM(oi.revenue), 0)                          AS total_revenue,
    COUNT(DISTINCT o.order_id)                         AS total_orders,
    COUNT(DISTINCT o.customer_id)                      AS active_customers,
    ROUND(SUM(oi.revenue) / COUNT(DISTINCT o.order_id), 0) AS avg_order_value
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered';


-- Q2. Category-wise revenue aur share (window function)
SELECT
    p.category,
    ROUND(SUM(oi.revenue), 0)                                        AS revenue,
    ROUND(100.0 * SUM(oi.revenue) / SUM(SUM(oi.revenue)) OVER (), 1) AS revenue_share_pct,
    RANK() OVER (ORDER BY SUM(oi.revenue) DESC)                      AS revenue_rank
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o   ON o.order_id   = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY p.category
ORDER BY revenue DESC;


-- Q3. Monthly revenue, MoM growth aur YoY growth (CTE + LAG)
-- PostgreSQL: DATE_TRUNC('month', order_date) | MySQL: DATE_FORMAT(order_date,'%Y-%m')
WITH monthly AS (
    SELECT
        STRFTIME('%Y-%m', o.order_date) AS month,
        SUM(oi.revenue)                 AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY 1
)
SELECT
    month,
    ROUND(revenue, 0) AS revenue,
    ROUND(100.0 * (revenue - LAG(revenue, 1)  OVER (ORDER BY month))
                / LAG(revenue, 1)  OVER (ORDER BY month), 1) AS mom_growth_pct,
    ROUND(100.0 * (revenue - LAG(revenue, 12) OVER (ORDER BY month))
                / LAG(revenue, 12) OVER (ORDER BY month), 1) AS yoy_growth_pct
FROM monthly
ORDER BY month;


-- Q4. Top 3 products har category mein (ROW_NUMBER + partition)
WITH product_rev AS (
    SELECT p.category, p.product_id, SUM(oi.revenue) AS revenue
    FROM order_items oi
    JOIN products p ON p.product_id = oi.product_id
    JOIN orders o   ON o.order_id   = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY p.category, p.product_id
),
ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC) AS rn
    FROM product_rev
)
SELECT category, product_id, ROUND(revenue, 0) AS revenue, rn AS rank_in_category
FROM ranked
WHERE rn <= 3
ORDER BY category, rn;


-- Q5. Repeat customer rate
WITH cust_orders AS (
    SELECT customer_id, COUNT(*) AS n_orders
    FROM orders
    WHERE order_status = 'delivered'
    GROUP BY customer_id
)
SELECT
    COUNT(*)                                             AS customers,
    SUM(CASE WHEN n_orders > 1 THEN 1 ELSE 0 END)        AS repeat_customers,
    ROUND(100.0 * SUM(CASE WHEN n_orders > 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS repeat_rate_pct
FROM cust_orders;


-- Q6. Top 10 customers by lifetime value + running share of revenue
WITH clv AS (
    SELECT o.customer_id, SUM(oi.revenue) AS lifetime_value, COUNT(DISTINCT o.order_id) AS orders
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY o.customer_id
)
SELECT
    customer_id,
    orders,
    ROUND(lifetime_value, 0) AS lifetime_value,
    ROUND(100.0 * SUM(lifetime_value) OVER (ORDER BY lifetime_value DESC)
                / SUM(lifetime_value) OVER (), 1) AS cumulative_revenue_pct
FROM clv
ORDER BY lifetime_value DESC
LIMIT 10;


-- Q7. Delivery delay ka review rating par asar
SELECT
    CASE
        WHEN delay_days <= 0 THEN '1. On time / early'
        WHEN delay_days <= 2 THEN '2. 1-2 days late'
        WHEN delay_days <= 5 THEN '3. 3-5 days late'
        ELSE                      '4. 6+ days late'
    END AS delivery_bucket,
    COUNT(*)                     AS orders,
    ROUND(AVG(review_rating), 2) AS avg_rating
FROM orders
WHERE order_status = 'delivered' AND delay_days IS NOT NULL
GROUP BY 1
ORDER BY 1;


-- Q8. City-wise performance
SELECT
    c.city,
    COUNT(DISTINCT o.order_id)               AS orders,
    ROUND(SUM(oi.revenue), 0)                AS revenue,
    ROUND(AVG(o.delivery_days), 1)           AS avg_delivery_days
FROM orders o
JOIN customers c    ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id   = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.city
ORDER BY revenue DESC;


-- Q9. Cohort retention: signup month ke hisaab se kitne % customers ne dobara order kiya
WITH first_order AS (
    SELECT customer_id, MIN(order_date) AS first_date
    FROM orders WHERE order_status = 'delivered'
    GROUP BY customer_id
),
cohort AS (
    SELECT
        STRFTIME('%Y-%m', f.first_date) AS cohort_month,
        o.customer_id,
        CAST((JULIANDAY(o.order_date) - JULIANDAY(f.first_date)) / 30 AS INT) AS months_since_first
    FROM orders o
    JOIN first_order f ON f.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
)
SELECT
    cohort_month,
    COUNT(DISTINCT CASE WHEN months_since_first = 0 THEN customer_id END) AS cohort_size,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_first BETWEEN 1 AND 3 THEN customer_id END)
          / NULLIF(COUNT(DISTINCT CASE WHEN months_since_first = 0 THEN customer_id END), 0), 1) AS retained_1_3m_pct
FROM cohort
GROUP BY cohort_month
ORDER BY cohort_month;


-- Q10. Discount ka revenue aur order size par asar
SELECT
    discount,
    COUNT(*)                          AS line_items,
    ROUND(AVG(quantity), 2)           AS avg_qty,
    ROUND(SUM(revenue), 0)            AS revenue
FROM order_items
GROUP BY discount
ORDER BY discount;
