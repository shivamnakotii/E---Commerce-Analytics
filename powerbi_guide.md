# Power BI / Tableau Dashboard Guide

## 1. Data load karo
Power BI Desktop > Get Data > Text/CSV, yeh files import karo (`data/processed/`):

| File | Use |
|---|---|
| `bi_sales_fact.csv` | Main fact table (order line level) |
| `customers_clean.csv` | Customer dimension |
| `products_clean.csv` | Product dimension |
| `../../outputs/rfm_segments.csv` | RFM segment per customer |

**Model view mein relationships:**
- `bi_sales_fact[customer_id]` → `customers_clean[customer_id]` (Many-to-One)
- `bi_sales_fact[customer_id]` → `rfm_segments[customer_id]` (Many-to-One)
- `bi_sales_fact[product_id]` → `products_clean[product_id]` (Many-to-One)

Ek **Date table** banao (Modeling > New table):
```DAX
Date = CALENDAR(DATE(2023,1,1), DATE(2024,12,31))
```
Phir `Date[Date]` ko `bi_sales_fact[order_date]` se jodo, aur Date table ko "Mark as date table" karo.

## 2. DAX Measures

```DAX
Total Revenue = SUM(bi_sales_fact[revenue])

Total Orders = DISTINCTCOUNT(bi_sales_fact[order_id])

Active Customers = DISTINCTCOUNT(bi_sales_fact[customer_id])

Avg Order Value = DIVIDE([Total Revenue], [Total Orders])

Revenue LY = CALCULATE([Total Revenue], SAMEPERIODLASTYEAR('Date'[Date]))

YoY Growth % = DIVIDE([Total Revenue] - [Revenue LY], [Revenue LY])

Revenue MoM % =
VAR prev = CALCULATE([Total Revenue], DATEADD('Date'[Date], -1, MONTH))
RETURN DIVIDE([Total Revenue] - prev, prev)

Late Delivery % =
DIVIDE(
    CALCULATE(DISTINCTCOUNT(bi_sales_fact[order_id]), bi_sales_fact[delay_days] > 0),
    [Total Orders]
)

Avg Rating = AVERAGE(bi_sales_fact[review_rating])

Repeat Customers =
COUNTROWS(
    FILTER(
        VALUES(bi_sales_fact[customer_id]),
        CALCULATE(DISTINCTCOUNT(bi_sales_fact[order_id])) > 1
    )
)

Repeat Rate % = DIVIDE([Repeat Customers], [Active Customers])
```

## 3. Dashboard layout (3 pages)

### Page 1: Executive Overview
- **Top row (KPI cards):** Total Revenue, Orders, Active Customers, AOV, YoY Growth %
- **Line chart:** Revenue by month (Axis = Date[Month Year])
- **Bar chart:** Revenue by category
- **Map / bar:** Revenue by city
- **Slicers:** Year, Category, City

### Page 2: Customer Segmentation
- **Donut / bar:** Customers by RFM segment
- **Bar:** Revenue by segment
- **Table:** Segment | Customers | Avg spend | Recommended action
- **Scatter:** Recency vs Monetary (Legend = segment)

### Page 3: Delivery & Satisfaction
- **KPI cards:** Late Delivery %, Avg Rating
- **Column chart:** Avg Rating by delay bucket (calculated column neeche)
- **Line:** Late Delivery % by month
- **Table:** City | Avg delay | Avg rating

Delay bucket calculated column:
```DAX
Delay Bucket =
SWITCH(
    TRUE(),
    bi_sales_fact[delay_days] <= 0, "1. On time",
    bi_sales_fact[delay_days] <= 2, "2. 1-2 days late",
    bi_sales_fact[delay_days] <= 5, "3. 3-5 days late",
    "4. 6+ days late"
)
```

## 4. Design tips
- 1 theme, 3-4 colours max. Titles mein insight likho ("Electronics 51% revenue deta hai") sirf "Revenue by category" nahi.
- KPI cards sabse upar, details neeche.
- Consistent number format (₹ lakh / crore).
- Mobile layout bhi banao (View > Mobile layout).
- Publish to Power BI Service aur public link ya screenshot GitHub README mein daalo.

## 5. Tableau users ke liye
Same CSVs connect karo. Calculated field example (Late flag):
```
IF [delay_days] > 0 THEN "Late" ELSE "On time" END
```
Revenue YoY: Quick Table Calculation > Year over Year Growth.
