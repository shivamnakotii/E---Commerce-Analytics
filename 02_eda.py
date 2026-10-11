"""
Step 2: Exploratory analysis + charts (Matplotlib / Seaborn)
Output: outputs/charts/*.png aur outputs/kpis.json
"""
import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from config import PROCESSED, CHARTS, OUTPUTS

sns.set_theme(style="whitegrid", context="talk")
PALETTE = "viridis"

customers = pd.read_csv(PROCESSED / "customers_clean.csv")
products = pd.read_csv(PROCESSED / "products_clean.csv")
orders = pd.read_csv(
    PROCESSED / "orders_clean.csv",
    parse_dates=["order_date", "estimated_delivery_date", "delivered_date"],
)
items = pd.read_csv(PROCESSED / "order_items_clean.csv")

delivered = orders[orders["order_status"] == "delivered"]
df = (
    items.merge(delivered, on="order_id")
    .merge(products[["product_id", "category"]], on="product_id")
    .merge(customers[["customer_id", "city"]], on="customer_id")
)
df["month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()


def inr_lakh(x, _):
    return f"₹{x / 1e5:.0f}L"


def save(fig, name):
    fig.tight_layout()
    fig.savefig(CHARTS / name, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print("saved", name)


# ---------- KPIs ----------
total_rev = df["revenue"].sum()
n_orders = df["order_id"].nunique()
kpis = {
    "total_revenue": round(float(total_rev), 0),
    "total_orders": int(n_orders),
    "active_customers": int(df["customer_id"].nunique()),
    "avg_order_value": round(float(total_rev / n_orders), 0),
    "late_delivery_pct": round(float(delivered["is_late"].mean() * 100), 1),
    "avg_rating": round(float(delivered["review_rating"].mean()), 2),
    "cancel_or_return_pct": round(float((orders["order_status"] != "delivered").mean() * 100), 1),
}
(OUTPUTS / "kpis.json").write_text(json.dumps(kpis, indent=2), encoding="utf-8")
print(kpis)

# ---------- 1. Monthly revenue trend ----------
monthly = df.groupby("month")["revenue"].sum()
fig, ax = plt.subplots(figsize=(13, 5.5))
ax.plot(monthly.index, monthly.values, marker="o", linewidth=2.5, color="#2a9d8f")
ax.fill_between(monthly.index, monthly.values, alpha=0.15, color="#2a9d8f")
peak = monthly.idxmax()
ax.annotate(f"Peak: {peak:%b %Y}", (peak, monthly.max()),
            xytext=(-130, -45), textcoords="offset points",
            arrowprops=dict(arrowstyle="->"), fontsize=12)
ax.yaxis.set_major_formatter(mtick.FuncFormatter(inr_lakh))
ax.set_title("Monthly Revenue Trend (Delivered Orders)")
ax.set_xlabel("")
ax.set_ylabel("Revenue")
save(fig, "01_monthly_revenue.png")

# ---------- 2. Revenue by category ----------
cat = df.groupby("category")["revenue"].sum().sort_values()
fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.barh(cat.index, cat.values, color=sns.color_palette(PALETTE, len(cat)))
for b, v in zip(bars, cat.values):
    ax.text(v, b.get_y() + b.get_height() / 2, f" {v / total_rev:.0%}", va="center", fontsize=12)
ax.xaxis.set_major_formatter(mtick.FuncFormatter(inr_lakh))
ax.set_title("Revenue by Category (share %)")
save(fig, "02_category_revenue.png")

# ---------- 3. Seasonality: avg revenue per calendar month ----------
season = df.assign(m=df["order_date"].dt.month).groupby("m")["revenue"].sum()
season = season / season.mean()
fig, ax = plt.subplots(figsize=(12, 5))
colors = ["#e76f51" if v > 1.15 else "#8ab6b0" for v in season.values]
ax.bar(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
       season.values, color=colors)
ax.axhline(1, color="grey", linestyle="--", linewidth=1)
ax.set_title("Seasonality Index (1.0 = average month)")
save(fig, "03_seasonality.png")

# ---------- 4. Delivery delay vs rating ----------
d = delivered.dropna(subset=["delay_days", "review_rating"]).copy()
d["bucket"] = pd.cut(d["delay_days"], [-100, 0, 2, 5, 100],
                     labels=["On time", "1-2 days late", "3-5 days late", "6+ days late"])
r = d.groupby("bucket", observed=True)["review_rating"].mean()
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.bar(r.index.astype(str), r.values, color=["#2a9d8f", "#e9c46a", "#f4a261", "#e76f51"])
for i, v in enumerate(r.values):
    ax.text(i, v + 0.05, f"{v:.2f}", ha="center", fontsize=13)
ax.set_ylim(0, 5)
ax.set_ylabel("Average rating")
ax.set_title("Late Delivery Hurts Ratings")
save(fig, "04_delay_vs_rating.png")
corr = d["delay_days"].corr(d["review_rating"])
print(f"delay vs rating correlation: {corr:.2f}")

# ---------- 5. City revenue ----------
city = df.groupby("city")["revenue"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(12, 5.5))
sns.barplot(x=city.index, y=city.values, hue=city.index, palette="mako_r", legend=False, ax=ax)
ax.yaxis.set_major_formatter(mtick.FuncFormatter(inr_lakh))
ax.set_title("Revenue by City")
ax.set_xlabel("")
plt.setp(ax.get_xticklabels(), rotation=35, ha="right")
save(fig, "05_city_revenue.png")

# ---------- 6. Order value distribution ----------
aov = df.groupby("order_id")["revenue"].sum()
fig, ax = plt.subplots(figsize=(11, 5))
sns.histplot(aov[aov < aov.quantile(0.98)], bins=40, color="#264653", ax=ax)
ax.axvline(aov.median(), color="#e76f51", linestyle="--", label=f"Median ₹{aov.median():,.0f}")
ax.legend()
ax.set_title("Order Value Distribution (top 2% outliers hidden)")
ax.set_xlabel("Order value (₹)")
save(fig, "06_order_value_distribution.png")

# ---------- Export tables for BI dashboards ----------
bi = df[["order_id", "customer_id", "city", "category", "product_id", "month",
         "order_date", "quantity", "discount", "revenue", "delay_days", "review_rating"]]
bi.to_csv(PROCESSED / "bi_sales_fact.csv", index=False)
monthly.reset_index().to_csv(PROCESSED / "bi_monthly_revenue.csv", index=False)
print("BI export ready")
