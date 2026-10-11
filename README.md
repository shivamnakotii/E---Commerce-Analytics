# 🛒 E-commerce Sales & Customer Segmentation (RFM) Analysis

End-to-end Data Analyst portfolio project: **Python + SQL + Power BI/Tableau**.

> **Business problem:** Ek online retailer ko samajhna hai ki revenue kahan se aa raha hai,
> kab badhta hai, kaun se customers sabse valuable hain, aur kaun churn hone wale hain,
> taaki marketing aur delivery decisions data se liye ja sakein.

---

## 📁 Project Structure

```
ecommerce-sales-analysis/
├── data/
│   ├── raw/                 # customers, products, orders, order_items (dirty data)
│   └── processed/           # clean CSVs, SQLite DB, BI-ready files
├── sql/
│   ├── schema.sql           # table structure + indexes
│   └── analysis_queries.sql # 10 business queries (joins, CTE, window functions)
├── src/
│   ├── generate_data.py     # synthetic data generator
│   ├── 01_cleaning.py       # data cleaning
│   ├── 02_eda.py            # EDA + charts + KPIs
│   ├── 03_rfm.py            # RFM segmentation
│   └── run_sql.py           # runs all SQL queries on SQLite
├── outputs/
│   ├── charts/              # 8 PNG charts
│   ├── kpis.json, rfm_segments.csv, rfm_summary.csv, sql_results.txt
├── dashboard/
│   └── index.html           # interactive colorful dashboard (browser mein kholo)
├── docs/
│   ├── insights_report.md   # findings + recommendations
│   └── powerbi_guide.md     # dashboard build guide (DAX included)
├── run_all.py               # ek command mein poora pipeline
└── requirements.txt
```

## ✨ Interactive Dashboard

`dashboard/index.html` ko browser mein double-click karke kholo: animated KPIs, sliding tabs,
morphing shapes, interactive charts aur clickable customer-segment bubbles. Internet chahiye (Chart.js aur fonts CDN se aate hain).

## 🚀 Kaise chalayein

```bash
pip install -r requirements.txt
python run_all.py
```

Yeh data generate karega, clean karega, SQL queries chalayega, charts banayega aur RFM segments nikalega.
Har script alag se bhi chal sakti hai (`cd src && python 01_cleaning.py`).

## 📊 Dataset ke baare mein

Is repo mein **synthetic dataset** hai (3,000 customers, 250 products, ~10.7k orders, 2023-2024)
jo Olist-style schema follow karta hai. Isme jaan-bujhkar duplicates, missing values, negative quantity
aur inconsistent city names daale gaye hain taaki cleaning step real lage.

**Real dataset use karna ho (recommended for final portfolio):**
1. Kaggle se [Olist Brazilian E-commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) download karo.
2. `data/raw/` mein CSVs rakho aur column names is mapping se rename karo:

| Is project ka column | Olist column |
|---|---|
| `customer_id` | `customer_unique_id` |
| `order_date` | `order_purchase_timestamp` |
| `estimated_delivery_date` | `order_estimated_delivery_date` |
| `delivered_date` | `order_delivered_customer_date` |
| `unit_price` | `price` (order_items) |
| `review_rating` | `review_score` (order_reviews) |

3. `generate_data.py` skip karo, baaki scripts same chalengi. (Olist mein `quantity` aur `discount` nahi hota: quantity = 1 aur discount = 0 maan lo.)

## 🧰 Skills jo yeh project dikhata hai

| Skill | Kahan |
|---|---|
| Data cleaning (Pandas) | `01_cleaning.py` |
| SQL: joins, CTE, window functions (RANK, LAG, ROW_NUMBER), cohort analysis | `sql/analysis_queries.sql` |
| EDA & visualization | `02_eda.py` |
| Customer segmentation (RFM) | `03_rfm.py` |
| Dashboarding & DAX | `docs/powerbi_guide.md` |
| Business storytelling | `docs/insights_report.md` |

## 🔍 Key Findings (synthetic data par)

- **Electronics** akela ~51% revenue deta hai, top 2 categories milake ~70%.
- **Oct-Dec** mein seasonality index 1.4-1.8x hai (Diwali + year-end sale), Jan-Feb sabse weak.
- **Champions** (23% customers) ~52% revenue laate hain.
- Delivery 3-5 din late hone par avg rating **4.4 se girkar ~3.3** ho jaati hai.
- ~36% orders estimated date se late deliver hue.

Poori detail `docs/insights_report.md` mein hai.

## 📝 Resume mein kaise likhein

> *Analysed 10K+ e-commerce orders (₹8.1 Cr revenue) using Python, SQL and Power BI; built RFM segmentation
> that showed 23% of customers drive 52% of revenue, and identified late delivery as the main driver of
> low ratings (4.4 → 3.3), with retention and logistics recommendations.*

(Real dataset use karo to numbers apne results se update karna.)

## 🔮 Next steps

- Churn prediction model (Logistic Regression / Random Forest)
- Sales forecasting (Prophet / SARIMA)
- Market basket analysis (Apriori)
- Streamlit app banakar deploy karo
