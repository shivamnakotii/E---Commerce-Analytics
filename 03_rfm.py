"""
Step 3: RFM customer segmentation
Recency   = last order kitne din pehle tha
Frequency = kitne orders kiye
Monetary  = kitna paisa kharch kiya
Har metric ko 1-5 score do (5 = best), phir segment rules lagao.
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from config import PROCESSED, CHARTS, OUTPUTS

sns.set_theme(style="whitegrid", context="talk")

orders = pd.read_csv(PROCESSED / "orders_clean.csv", parse_dates=["order_date"])
items = pd.read_csv(PROCESSED / "order_items_clean.csv")

d = items.merge(orders[orders["order_status"] == "delivered"], on="order_id")
snapshot = d["order_date"].max() + pd.Timedelta(days=1)

rfm = d.groupby("customer_id").agg(
    recency=("order_date", lambda x: (snapshot - x.max()).days),
    frequency=("order_id", "nunique"),
    monetary=("revenue", "sum"),
).reset_index()

# Scores (quintiles). Frequency mein rank(method="first") isliye ki ties na tootein.
rfm["R"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
rfm["F"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm["M"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm["rfm_score"] = rfm["R"].astype(str) + rfm["F"].astype(str) + rfm["M"].astype(str)


def segment(r):
    R, F, M = r["R"], r["F"], r["M"]
    fm = (F + M) / 2
    if R >= 4 and fm >= 4:
        return "Champions"
    if R >= 3 and fm >= 3:
        return "Loyal Customers"
    if R >= 4 and fm < 3:
        return "New / Promising"
    if R <= 2 and fm >= 4:
        return "Can't Lose Them"
    if R <= 2 and fm >= 3:
        return "At Risk"
    if R <= 2:
        return "Lost"
    return "Need Attention"


rfm["segment"] = rfm.apply(segment, axis=1)

action = {
    "Champions": "Reward karo: early access, loyalty points, referral program",
    "Loyal Customers": "Upsell / cross-sell, membership offer",
    "New / Promising": "Onboarding emails, doosre order par discount",
    "Need Attention": "Personalised recommendations, limited-time offer",
    "At Risk": "Win-back email + discount coupon",
    "Can't Lose Them": "Personal outreach, premium offer, feedback call",
    "Lost": "Low-cost reactivation campaign, ya ignore karo",
}
rfm["recommended_action"] = rfm["segment"].map(action)
rfm.to_csv(OUTPUTS / "rfm_segments.csv", index=False)

summary = rfm.groupby("segment").agg(
    customers=("customer_id", "count"),
    avg_recency_days=("recency", "mean"),
    avg_orders=("frequency", "mean"),
    avg_spend=("monetary", "mean"),
    total_revenue=("monetary", "sum"),
).round(1)
summary["customer_pct"] = (100 * summary["customers"] / summary["customers"].sum()).round(1)
summary["revenue_pct"] = (100 * summary["total_revenue"] / summary["total_revenue"].sum()).round(1)
summary = summary.sort_values("total_revenue", ascending=False)
summary.to_csv(OUTPUTS / "rfm_summary.csv")
print(summary.to_string())

# ---------- Charts ----------
order = summary.index.tolist()
colors = sns.color_palette("viridis", len(order))

fig, axes = plt.subplots(1, 2, figsize=(15, 6))
sns.barplot(x=summary["customers"], y=summary.index, hue=summary.index,
            palette=colors, legend=False, ax=axes[0])
axes[0].set_title("Customers per Segment")
axes[0].set_ylabel("")
axes[0].set_xlabel("")
sns.barplot(x=summary["revenue_pct"], y=summary.index, hue=summary.index,
            palette=colors, legend=False, ax=axes[1])
axes[1].set_title("Revenue Share per Segment (%)")
axes[1].set_ylabel("")
axes[1].set_xlabel("")
axes[1].set_yticklabels([])
fig.tight_layout()
fig.savefig(CHARTS / "07_rfm_segments.png", dpi=130, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(11, 7))
sns.scatterplot(data=rfm, x="recency", y="monetary", hue="segment", size="frequency",
                sizes=(20, 220), alpha=0.6, ax=ax)
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"₹{x / 1e3:.0f}k"))
ax.set_xlabel("Recency (days since last order)")
ax.set_ylabel("Total spend")
ax.set_title("RFM Map: Recency vs Spend")
ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=10)
fig.tight_layout()
fig.savefig(CHARTS / "08_rfm_scatter.png", dpi=130, bbox_inches="tight")
plt.close(fig)
print("RFM charts saved")
