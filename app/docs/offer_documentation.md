
# 📝 Offer Creation – Simple Overview

## 🎯 What it does:
Allows users to **create or update offers** for a group of customers based on their segmentation.
---
## 🧾 Input by User:
- `zid`: Branch ID
- `xtitle`: Segment name (e.g., "Developing")
- Offer values:
  - `xcreditr`: Offer description (e.g., "Free T-Shirt")
  - `xmonper`: Extra sale percentage
  - `xmondiscper`: Discount percentage
  - `xisgotmon`: Did they get monitoring offer? (`'true'` or `'false'`)
  - `xisgotdefault`: Did they get default offer? (`'true'` or `'false'`)

> Note: `"Developing"` will match `"Developing-1"`, `"Developing-2"`, etc.

---

## 🔍 How it works:
1. Find all customers with matching `zid` and segment
2. Update their offer fields in bulk
3. Save changes to database
4. Show how many customers were updated

---

## ✅ Success Example:
```
Successfully updated 15 customers in zid 100001
Offer: Free T-Shirt
```

---

## ❌ If No Match Found:
```
No customers found in zid 100001 and segment: Developing
```

---
## 💡 Summary:
This system helps assign offers quickly to groups of customers using segmentation.




```

```



# 📄 Offer eligibility Logic 

## 🎯 How It Works

This system calculates how much a customer has spent after returns, and decides whether they qualify for an offer.

### ✅ Net Sales
Net sales = Total sales – Returns  
(Returns include both types: Imtemptrn and Opcrn)

### 🧮 Avg Per Order Net Sales
We calculate:
> Average net sale per order = Yearly net sales ÷ Number of orders

### 🎯 Monthly Target
The system sets a monthly target using this formula:
> Monthly Target = Average net sale per order + xmonper%

- `xmonper` is a percentage stored in the cacus table.
- Example: If average sale is 50,000 and `xmonper = 10`, then target = **55,000**

### 💰 Discount Offer (`xmondiscper`)
This is the discount the customer can get if they meet the monthly target.

If customer **meets or exceeds** the target:
> "You will get X% discount on your next purchase"

If customer **does not meet** the target:
> "You are Tk- Y away from getting X% discount"

### ✅ Did They Already Get the Offer?

We check two flags:

- `xisgotdefault`: Has the customer already received the default offer like `"Free T-Shirt"`?
- `xisgotmon`: Has the customer already received the monetary discount?

If either is `"true"`, the message becomes:
> "You already got the Free T-Shirt"  
or  
> "You already got the 2% discount"

---

## 📤 Final Output Example

```json
{
  "xcus": "CUS-000003",
  "xorg": "Rahima Enterprise",
  "xadd1": "Shasangasa, Comilla",

  "xmonper": 10,
  "xmondiscper": 2,
  "xcreditr": "Free Tshirt",

  "xisgotdefault": false,
  "xisgotmon": false,

  "yearly_net_sales": 17144847.18,
  "avg_per_order_net_sales": 52270.88,

  "this_month_net_sales": 820750,
  "this_month_target_sales": 57497.96,
  "sales_gap": -763252.04,

  "default_offer": "Free Tshirt",
  "monitory_offer": "You will get 2% discount on your next purchase",
  "offer": "You will get 2% discount on your next purchase"
}
```