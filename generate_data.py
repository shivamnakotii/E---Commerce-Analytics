"""
Synthetic e-commerce dataset generator (Olist-style schema).

Kaggle ka dataset use karna ho to is step ko skip karke apni CSV files
data/raw/ mein rakh do (README mein column mapping di gayi hai).
Yeh generator isliye hai taaki project internet ke bina bhi chale.
Data mein jaan-bujhkar kuch "ganda" data (duplicates, nulls, negative qty)
daala gaya hai taaki cleaning step meaningful ho.
"""
import numpy as np
import pandas as pd
from config import RAW

rng = np.random.default_rng(42)

N_CUSTOMERS = 3000
N_PRODUCTS = 250
START, END = pd.Timestamp("2023-01-01"), pd.Timestamp("2024-12-31")

# ---------------- Customers ----------------
cities = {
    "Delhi": "Delhi", "Mumbai": "Maharashtra", "Pune": "Maharashtra",
    "Bengaluru": "Karnataka", "Hyderabad": "Telangana", "Chennai": "Tamil Nadu",
    "Kolkata": "West Bengal", "Ahmedabad": "Gujarat", "Jaipur": "Rajasthan",
    "Lucknow": "Uttar Pradesh", "Chandigarh": "Chandigarh", "Patna": "Bihar",
}
city_names = list(cities)
city_w = np.array([14, 14, 7, 13, 9, 9, 8, 6, 5, 5, 5, 5], dtype=float)
city_w /= city_w.sum()

customers = pd.DataFrame({
    "customer_id": [f"C{str(i).zfill(5)}" for i in range(1, N_CUSTOMERS + 1)],
    "city": rng.choice(city_names, N_CUSTOMERS, p=city_w),
})
customers["state"] = customers["city"].map(cities)
# 65% customers pehle 3 mahine mein aaye (established base), baaki dheere-dheere
early = rng.random(N_CUSTOMERS) < 0.65
signup_days = np.where(early, rng.integers(0, 90, N_CUSTOMERS), rng.integers(0, 700, N_CUSTOMERS))
customers["signup_date"] = START + pd.to_timedelta(signup_days, unit="D")

# ---------------- Products ----------------
categories = {
    "Electronics": (3000, 40000), "Fashion": (400, 4000), "Home & Kitchen": (300, 8000),
    "Beauty": (150, 2500), "Books": (100, 900), "Sports": (500, 9000),
    "Toys": (200, 3000), "Grocery": (50, 1200),
}
cat_names = list(categories)
cat_w = np.array([10, 22, 16, 14, 10, 8, 10, 10], dtype=float)
cat_w /= cat_w.sum()
prod_cat = rng.choice(cat_names, N_PRODUCTS, p=cat_w)
prod_price = [max(10.0, round(float(rng.uniform(*categories[c])), -1)) for c in prod_cat]
products = pd.DataFrame({
    "product_id": [f"P{str(i).zfill(4)}" for i in range(1, N_PRODUCTS + 1)],
    "category": prod_cat,
    "price": prod_price,
})

# ---------------- Customer behaviour ----------------
# 0 = champions, 1 = regular, 2 = occasional, 3 = one-timers
seg = rng.choice([0, 1, 2, 3], N_CUSTOMERS, p=[0.10, 0.25, 0.30, 0.35])
orders_per_cust = np.select(
    [seg == 0, seg == 1, seg == 2, seg == 3],
    [rng.integers(8, 16, N_CUSTOMERS), rng.integers(4, 8, N_CUSTOMERS),
     rng.integers(2, 4, N_CUSTOMERS), np.ones(N_CUSTOMERS, dtype=int)],
)
# churn: kuch customers ek date ke baad gayab ho jaate hain
churned = rng.random(N_CUSTOMERS) < np.where(seg >= 2, 0.45, 0.10)

# monthly seasonality (Oct-Nov Diwali, Dec sale, Jan-Feb low)
month_w = {1: .8, 2: .75, 3: .9, 4: .9, 5: .95, 6: .9, 7: 1.0, 8: 1.05, 9: 1.1, 10: 1.6, 11: 1.7, 12: 1.3}

all_days = pd.date_range(START, END)
day_w = np.array([month_w[d.month] * (1 + 0.15 * (d.year == 2024)) for d in all_days])

prod_idx = np.arange(N_PRODUCTS)
order_rows, item_rows = [], []
oid = 0
for i, cid in enumerate(customers["customer_id"]):
    n = int(orders_per_cust[i])
    signup = customers.loc[i, "signup_date"]
    last_active = pd.Timestamp("2024-06-30") if churned[i] else END
    pool_mask = (all_days >= signup) & (all_days <= last_active)
    if pool_mask.sum() < 5:
        continue
    w = day_w[pool_mask] / day_w[pool_mask].sum()
    dates = rng.choice(all_days[pool_mask], n, p=w)
    for d in dates:
        oid += 1
        order_id = f"O{str(oid).zfill(6)}"
        d = pd.Timestamp(d)
        est_days = int(rng.integers(4, 9))
        base_delay = rng.normal(-0.7, 2.0) + (1.2 if d.month in (10, 11, 12) else 0)
        actual_days = max(2, int(round(est_days + base_delay)))
        status = rng.choice(["delivered", "cancelled", "returned"], p=[0.93, 0.04, 0.03])
        delay = actual_days - est_days
        # rating delay se negatively correlated
        rating = int(np.clip(round(rng.normal(4.5 - 0.35 * max(delay, 0), 0.7)), 1, 5))
        order_rows.append({
            "order_id": order_id, "customer_id": cid, "order_date": d,
            "estimated_delivery_date": d + pd.Timedelta(days=est_days),
            "delivered_date": d + pd.Timedelta(days=actual_days) if status == "delivered" else pd.NaT,
            "order_status": status,
            "review_rating": rating if status == "delivered" else np.nan,
        })
        n_items = int(rng.choice([1, 2, 3, 4], p=[0.6, 0.25, 0.1, 0.05]))
        for pi in rng.choice(prod_idx, n_items, replace=False):
            disc = float(rng.choice([0, 0.05, 0.1, 0.2], p=[0.5, 0.2, 0.2, 0.1]))
            item_rows.append({
                "order_id": order_id, "product_id": products.at[pi, "product_id"],
                "quantity": int(rng.choice([1, 2, 3], p=[0.8, 0.15, 0.05])),
                "unit_price": products.at[pi, "price"], "discount": disc,
            })

orders = pd.DataFrame(order_rows)
items = pd.DataFrame(item_rows)

# ---------------- Dirty data inject (cleaning practice) ----------------
dup = orders.sample(40, random_state=1)
orders = pd.concat([orders, dup], ignore_index=True)                        # duplicate orders
orders.loc[orders.sample(60, random_state=2).index, "customer_id"] = None     # missing customer
items.loc[items.sample(25, random_state=3).index, "quantity"] = -1            # invalid qty
items.loc[items.sample(15, random_state=4).index, "unit_price"] = np.nan      # missing price
up_idx = customers.sample(50, random_state=5).index
customers.loc[up_idx, "city"] = customers.loc[up_idx, "city"].str.upper()     # inconsistent case
sp_idx = customers.sample(30, random_state=6).index
customers.loc[sp_idx, "city"] = " " + customers.loc[sp_idx, "city"] + " "     # extra spaces

orders = orders.sample(frac=1, random_state=7).reset_index(drop=True)

customers.to_csv(RAW / "customers.csv", index=False)
products.to_csv(RAW / "products.csv", index=False)
orders.to_csv(RAW / "orders.csv", index=False)
items.to_csv(RAW / "order_items.csv", index=False)

print(f"customers={len(customers)} products={len(products)} orders={len(orders)} items={len(items)}")
