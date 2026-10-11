"""
Step 1: Data cleaning (Pandas)
Raw CSVs -> clean CSVs + SQLite database (SQL practice ke liye).
"""
import sqlite3
import pandas as pd
from config import RAW, PROCESSED, DB_PATH

log = []


def note(msg):
    print(msg)
    log.append(msg)


customers = pd.read_csv(RAW / "customers.csv", parse_dates=["signup_date"])
products = pd.read_csv(RAW / "products.csv")
orders = pd.read_csv(
    RAW / "orders.csv",
    parse_dates=["order_date", "estimated_delivery_date", "delivered_date"],
)
items = pd.read_csv(RAW / "order_items.csv")

# ---------- Customers ----------
customers["city"] = customers["city"].str.strip().str.title()
before = len(customers)
customers = customers.drop_duplicates("customer_id")
note(f"customers: {before} -> {len(customers)} rows (city text standardised)")

# ---------- Orders ----------
before = len(orders)
orders = orders.drop_duplicates("order_id")
note(f"orders: removed {before - len(orders)} duplicate order_ids")

before = len(orders)
orders = orders.dropna(subset=["customer_id"])
note(f"orders: removed {before - len(orders)} rows with missing customer_id")

orders = orders[orders["customer_id"].isin(customers["customer_id"])]

# delivery metrics
orders["delivery_days"] = (orders["delivered_date"] - orders["order_date"]).dt.days
orders["delay_days"] = (orders["delivered_date"] - orders["estimated_delivery_date"]).dt.days
orders["is_late"] = (orders["delay_days"] > 0).astype("Int64")
orders.loc[orders["delivered_date"].isna(), ["is_late"]] = pd.NA

# ---------- Order items ----------
before = len(items)
items = items[items["quantity"] > 0]
note(f"order_items: removed {before - len(items)} rows with invalid quantity (<=0)")

before = len(items)
items = items.dropna(subset=["unit_price"])
note(f"order_items: removed {before - len(items)} rows with missing unit_price")

items = items[items["order_id"].isin(orders["order_id"])]
items["revenue"] = (items["quantity"] * items["unit_price"] * (1 - items["discount"])).round(2)

# ---------- Outlier check (IQR) ----------
q1, q3 = items["revenue"].quantile([0.25, 0.75])
upper = q3 + 3 * (q3 - q1)
n_out = int((items["revenue"] > upper).sum())
note(f"revenue outliers (> {upper:,.0f}): {n_out} rows flagged, kept (high-value electronics are genuine)")

# ---------- Save ----------
customers.to_csv(PROCESSED / "customers_clean.csv", index=False)
products.to_csv(PROCESSED / "products_clean.csv", index=False)
orders.to_csv(PROCESSED / "orders_clean.csv", index=False)
items.to_csv(PROCESSED / "order_items_clean.csv", index=False)

# SQLite DB banao taaki sql/ folder ki queries chala sako
if DB_PATH.exists():
    DB_PATH.unlink()
with sqlite3.connect(DB_PATH) as con:
    for name, df in [("customers", customers), ("products", products),
                     ("orders", orders), ("order_items", items)]:
        d = df.copy()
        for c in d.select_dtypes("datetime64[ns]").columns:
            d[c] = d[c].dt.strftime("%Y-%m-%d")
        d.to_sql(name, con, index=False)
note(f"SQLite database created: {DB_PATH.name}")

(PROCESSED / "cleaning_log.txt").write_text("\n".join(log), encoding="utf-8")
