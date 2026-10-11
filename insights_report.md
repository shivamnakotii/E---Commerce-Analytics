# Insights & Recommendations Report

**Period:** Jan 2023 - Dec 2024 | **Scope:** Delivered orders | **Data:** synthetic (Olist-style)

> Note: numbers synthetic data se aaye hain. Real dataset par chalane ke baad figures update kar lena.

## 1. Executive Summary

| KPI | Value |
|---|---|
| Total revenue | ₹8.11 Cr |
| Orders | 9,867 |
| Active customers | 2,826 |
| Average order value | ₹8,216 |
| Repeat customer rate | 64.7% |
| Late deliveries | 36.3% |
| Average rating | 4.19 / 5 |
| Cancelled + returned orders | 7.1% |

Revenue 2023 se 2024 mein ₹3.12 Cr se ₹4.98 Cr (**+60%**) hua. Growth strong hai, lekin
revenue kuch hi categories aur kuch hi customers par tika hua hai, aur delivery quality ratings ko khinch rahi hai.

## 2. Findings

### 2.1 Category concentration
- **Electronics = 51%** revenue, Home & Kitchen = 19%. Do categories milake ~70%.
- Books aur Grocery sirf ~1-2% hain: volume hai lekin margin/contribution kam.
- **Risk:** Electronics mein demand ya supply ka jhatka poore business ko hilaa sakta hai.

### 2.2 Seasonality
- Seasonality index: **Nov 1.82x, Oct 1.48x, Dec 1.40x**; Jan 0.50x aur Feb 0.58x sabse kamzor.
- Festive quarter (Oct-Dec) saal ke revenue ka bada hissa laata hai.

### 2.3 Customer value (RFM)

| Segment | Customers % | Revenue % | Action |
|---|---|---|---|
| Champions | 23.0% | 52.0% | Loyalty program, early access |
| Loyal Customers | 20.6% | 23.9% | Upsell, membership |
| At Risk | 8.3% | 7.9% | Win-back coupon |
| Can't Lose Them | 3.5% | 6.8% | Personal outreach |
| Lost | 28.0% | 6.0% | Low-cost reactivation |
| New / Promising | 7.9% | 1.7% | Onboarding, 2nd order offer |
| Need Attention | 8.7% | 1.6% | Personalised offers |

- Champions + Loyal = 44% customers, **~76% revenue**.
- **At Risk + Can't Lose Them** = 12% customers aur ~14.7% revenue: yeh sabse accha recovery opportunity hai,
  kyunki inka purchase history strong hai lekin recently active nahi hain.

### 2.4 Delivery aur customer satisfaction

| Delivery | Orders | Avg rating |
|---|---|---|
| On time / early | 6,289 | 4.42 |
| 1-2 days late | 2,661 | 3.98 |
| 3-5 days late | 890 | 3.27 |
| 6+ days late | 39 | 2.38 |

Delay aur rating ka correlation **-0.42** hai (moderate negative): jitna zyada late, utni kam rating.

### 2.5 Geography
Delhi, Mumbai aur Bengaluru top 3 cities hain (~42% revenue). Average delivery time sab cities mein ~7 din hai,
yaani issue city-specific nahi, system-wide hai.

## 3. Recommendations

1. **Retention (highest ROI):** At Risk + Can't Lose Them segments ko win-back email (10-15% coupon) bhejo.
   In dono segments ka historical revenue ~₹1.19 Cr hai; agar sirf 15% customers wapas aaye aur pehle jitna
   hi kharch karein, to lagbhag ₹18 lakh ka incremental revenue milega (illustrative estimate).
2. **Champions ko protect karo:** loyalty tier + early access to festive sale.
3. **Delivery SLA:** estimated delivery date ko realistic banao (under-promise, over-deliver) aur 3+ din late
   hone wale orders par proactive apology/compensation do.
4. **Festive readiness:** Sept se hi inventory aur logistics capacity badhao, kyunki Oct-Dec mein delay zyada hota hai.
5. **Diversify:** Home & Kitchen aur Sports mein bundle offers se Electronics par dependency ghatao.
6. **Jan-Feb slump:** post-festive "clearance" campaign ya subscription offers chalao.

## 4. Limitations
- Synthetic data: real-world noise, marketing spend, margin aur returns reasons available nahi.
- Revenue = quantity x price x (1 - discount); profit margin analysis possible nahi.
- RFM quintile-based hai: rules business ke hisaab se tune karne chahiye.
