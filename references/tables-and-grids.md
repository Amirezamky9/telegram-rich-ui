# Tables and Grids (Telegram Bot API 10.3)

Telegram Bot API 10.3 introduces native tabular rendering via `sendRichMessage`. Prior to 10.3, bots attempted tabular layouts using monospace ASCII art inside `<pre>` tags. Those monospace tables frequently distorted on narrow mobile screens due to lack of character wrapping, proportional font scaling, and missing cell borders.

The Bot API 10.3 table system renders structured grid cells natively in Telegram clients (Desktop, iOS, Android, and Web) with responsive horizontal scrolling or cell wrapping, clear border boundaries, alternating background fills, and cell alignment controls.

---

## Table Syntax & Attributes

Tables are written using standard HTML table markup inside the `rich_message.html` string or mapped to `InputRichBlockTable` in JSON block trees.

```html
<table bordered striped compact>
  <caption>Financial Summary (Q3 2026)</caption>
  <tr>
    <th>Department</th>
    <th align="center">Headcount</th>
    <th align="right">Budget (USD)</th>
  </tr>
  <tr>
    <td align="left">Engineering</td>
    <td align="center">42</td>
    <td align="right">$520,000</td>
  </tr>
  <tr>
    <td align="left">Design & Product</td>
    <td align="center">16</td>
    <td align="right">$185,000</td>
  </tr>
  <tr>
    <td colspan="2"><b>Total Allocated</b></td>
    <td align="right"><b>$705,000</b></td>
  </tr>
</table>
```

### Table Container Attributes

The root `<table>` tag supports three boolean presentation modifiers:

| Attribute | JSON Block Field | Description |
|:---|:---|:---|
| `bordered` | `has_borders: true` | Draws a crisp border grid around all outer edges and between cells. |
| `striped` | `is_striped: true` | Alternates background row shading (light zebra-striping) for readable row scanning. |
| `compact` | `is_compact: true` | Reduces vertical and horizontal cell padding to fit dense financial data on mobile screens. |

> **Best Practice:** Always include `compact` when displaying more than 3 columns or when row counts exceed 6. It prevents unnecessary vertical screen stretching.

### Table Element Hierarchy

- `<caption>`: Centered title text rendered directly above the table frame.
- `<tr>`: Defines a table row containing cells.
- `<th>`: Header cell. Renders text in bold with distinct header background fill and vertical center alignment by default.
- `<td>`: Standard body data cell.

### Cell Alignment Attributes

Both `<th>` and `<td>` accept horizontal and vertical alignment attributes:

| Attribute | Values | Default | Effect |
|:---|:---|:---|:---|
| `align` | `left`, `center`, `right` | `left` (LTR) / `right` (RTL) | Controls horizontal text alignment within the cell. Always align numbers to the `right` and status tags to the `center`. |
| `valign` | `top`, `middle`, `bottom` | `middle` | Controls vertical alignment within the cell, particularly useful when multi-line text is paired with single-line values. |

### Cell Spanning Attributes

- `colspan="N"`: Expands the cell horizontally across $N$ columns (maximum recommended: 20).
- `rowspan="N"`: Expands the cell vertically across $N$ rows (maximum recommended: 30).

### فارسی — ساختار و صفات جدول
- تگ `<table>` سه ویژگی کلیدی دارد:
  - `bordered`: ایجاد خطوط کادر دور سلول‌ها.
  - `striped`: راه‌راه کردن سطرهای جدول با پس‌زمینه یکی در میان برای خوانایی بهتر.
  - `compact`: فشرده‌سازی فاصله‌های داخلی (padding) سلول‌ها تا داده‌های مالی و آماری در صفحه کوچک گوشی بهتر جا شوند (در قالب جیسون فیلد `is_compact: true`).
- صفات `align="left|center|right"` تراز افقی و `valign="top|middle|bottom"` تراز عمودی متن سلول را تنظیم می‌کنند.
- اعداد و مبالغ مالی را همیشه با `align="right"` تراز کنید.

---

## Grid Consistency & Dimensional Invariants

Telegram's client layout engines require a mathematically consistent rectangular matrix. If row cell counts deviate due to miscalculated `colspan` or unhandled `rowspan` overlaps, clients may fail to render the table or drop into an unformatted raw text fallback.

### The Rectangular Invariant Rule

For any table with $C$ columns and $R$ rows:
$$\forall r \in [1, R], \quad \sum_{\text{cells in row } r} \text{effective\_width} = C$$

Where $\text{effective\_width}$ includes:
1. The cell's own `colspan` value (default: 1).
2. Any `rowspan` spanning into row $r$ from preceding rows $r' < r$.

```
Correct Grid (3 Columns):
Row 1: [ Cell A: colspan=1 ] [ Cell B: colspan=1 ] [ Cell C: colspan=1 ]  -> Total = 3
Row 2: [ Cell D: colspan=2                       ] [ Cell E: colspan=1 ]  -> Total = 3
Row 3: [ Cell F: colspan=1, rowspan=2 ] [ Cell G: colspan=1 ] [ Cell H ]  -> Total = 3
Row 4: [ (Cell F spans here)          ] [ Cell I: colspan=2            ]  -> Total = 3
```

### Common Grid Pitfalls to Avoid

1. **Over-spanning beyond table width:** Specifying `colspan="3"` in a 2-column table pushes row width to 3, causing column collapse.
2. **Missing cells under `rowspan`:** When cell $X$ on row 1 has `rowspan="2"`, row 2 must define one fewer cell. Adding the full count creates an invalid protruding cell on row 2.
3. **Empty rows:** Do not emit empty `<tr></tr>` tags; Telegram table parsers treat empty rows as structural errors.

### فارسی — قواعد شبکه و پایداری جدول
- ساختار ماتریس جدول باید در تمام سطرها مستطیلی و یکدست باشد.
- اگر یک سلول با `colspan="2"` دو ستون را ادغام کرد، مجموع طول آن سطر با سطرهای دیگر باید دقیقاً برابر بماند.
- هنگام استفاده از `rowspan="2"` در یک سطر، در سطر بعدی باید یک سلول کمتر تعریف کنید تا سلول بالایی در جای خالی آن قرار گیرد؛ در غیر این صورت جدول کج شده و کلاینت تلگرام ممکن است به رندر متنی خام سوئیچ کند.

---

## Worked Production Examples

### 1. Financial Invoice

```html
<table bordered striped compact>
  <caption>Invoice #INV-2026-8819</caption>
  <tr>
    <th align="left">Item</th>
    <th align="center">Qty</th>
    <th align="right">Unit Price</th>
    <th align="right">Amount</th>
  </tr>
  <tr>
    <td>Cloud Worker Compute (Tier 2)</td>
    <td align="center">2</td>
    <td align="right">$25.00</td>
    <td align="right">$50.00</td>
  </tr>
  <tr>
    <td>Database Storage (100 GB)</td>
    <td align="center">1</td>
    <td align="right">$15.00</td>
    <td align="right">$15.00</td>
  </tr>
  <tr>
    <td>Bandwidth Egress (1 TB)</td>
    <td align="center">3</td>
    <td align="right">$10.00</td>
    <td align="right">$30.00</td>
  </tr>
  <tr>
    <td colspan="3" align="right"><b>Subtotal</b></td>
    <td align="right">$95.00</td>
  </tr>
  <tr>
    <td colspan="3" align="right">VAT / Tax (10%)</td>
    <td align="right">$9.50</td>
  </tr>
  <tr>
    <td colspan="3" align="right"><b>Total Due (USD)</b></td>
    <td align="right"><b>$104.50</b></td>
  </tr>
</table>
```

### 2. E-Commerce Shopping Cart

```html
<table bordered compact>
  <caption>🛒 Active Shopping Cart</caption>
  <tr>
    <th align="left">Product</th>
    <th align="center">Size</th>
    <th align="center">Qty</th>
    <th align="right">Price</th>
  </tr>
  <tr>
    <td>Wireless Noise-Canceling Headphones</td>
    <td align="center">Black</td>
    <td align="center">1</td>
    <td align="right">$189.00</td>
  </tr>
  <tr>
    <td>Braided USB-C Cable (2m)</td>
    <td align="center">Grey</td>
    <td align="center">2</td>
    <td align="right">$38.00</td>
  </tr>
  <tr>
    <td colspan="2" align="left"><i>Promo Discount (WELCOME10)</i></td>
    <td align="center">-10%</td>
    <td align="right">-$22.70</td>
  </tr>
  <tr>
    <td colspan="3" align="right"><b>Estimated Total</b></td>
    <td align="right"><b>$204.30</b></td>
  </tr>
</table>
```

### 3. Order Tracking Summary (with `rowspan` and `valign`)

```html
<table bordered striped compact>
  <caption>Package Delivery Status</caption>
  <tr>
    <th align="left">Order Details</th>
    <th align="left">Information</th>
  </tr>
  <tr>
    <td>Order ID</td>
    <td><code>#ORD-90421</code></td>
  </tr>
  <tr>
    <td rowspan="2" valign="top">Shipping Destination</td>
    <td>452 Freedom Avenue, Suite 12</td>
  </tr>
  <tr>
    <td>Tehran, Postal Code 14155</td>
  </tr>
  <tr>
    <td>Courier Service</td>
    <td>Express Courier (Tracking: <code>TRK-88190</code>)</td>
  </tr>
  <tr>
    <td>Estimated Arrival</td>
    <td><tg-time unix="1773660000" format="wDT">Tomorrow 16:00</tg-time></td>
  </tr>
  <tr>
    <td>Delivery Status</td>
    <td><b>In Transit (Out for Delivery)</b></td>
  </tr>
</table>
```

### 4. SaaS Feature Matrix / Tier Comparison

```html
<table bordered striped compact>
  <caption>Plan Feature Comparison</caption>
  <tr>
    <th align="left">Capability</th>
    <th align="center">Free</th>
    <th align="center">Pro</th>
    <th align="center">Enterprise</th>
  </tr>
  <tr>
    <td>Rich Messages</td>
    <td align="center">500 / mo</td>
    <td align="center">50,000 / mo</td>
    <td align="center">Unlimited</td>
  </tr>
  <tr>
    <td>Compact Tables</td>
    <td align="center">Yes</td>
    <td align="center">Yes</td>
    <td align="center">Yes</td>
  </tr>
  <tr>
    <td>Custom Emojis</td>
    <td align="center">Fallback only</td>
    <td align="center">Yes</td>
    <td align="center">Yes</td>
  </tr>
  <tr>
    <td>Dedicated SLA</td>
    <td align="center">Community</td>
    <td align="center">24h Email</td>
    <td align="center">1h 24/7 Phone</td>
  </tr>
  <tr>
    <td>Monthly Fee</td>
    <td align="center"><b>$0</b></td>
    <td align="center"><b>$29</b></td>
    <td align="center"><b>$199</b></td>
  </tr>
</table>
```

### 5. Cryptocurrency / FX Market Price List

```html
<table bordered striped compact>
  <caption>Live Market Tickers</caption>
  <tr>
    <th align="left">Asset</th>
    <th align="right">Price (USD)</th>
    <th align="right">24h Change</th>
    <th align="center">Signal</th>
  </tr>
  <tr>
    <td><b>TON</b> (Toncoin)</td>
    <td align="right">$6.85</td>
    <td align="right">+4.82%</td>
    <td align="center">BUY</td>
  </tr>
  <tr>
    <td><b>BTC</b> (Bitcoin)</td>
    <td align="right">$94,250.00</td>
    <td align="right">+1.15%</td>
    <td align="center">HOLD</td>
  </tr>
  <tr>
    <td><b>ETH</b> (Ethereum)</td>
    <td align="right">$3,420.50</td>
    <td align="right">-0.64%</td>
    <td align="center">HOLD</td>
  </tr>
  <tr>
    <td><b>SOL</b> (Solana)</td>
    <td align="right">$198.40</td>
    <td align="right">+7.30%</td>
    <td align="center">BUY</td>
  </tr>
</table>
```

---

## Block JSON Representation (`InputRichBlockTable`)

When submitting rich messages using the `blocks` parameter rather than raw HTML strings, tables are serialized into typed JSON objects:

```json
{
  "type": "table",
  "has_borders": true,
  "is_striped": true,
  "is_compact": true,
  "caption": {
    "text": "Product Inventory"
  },
  "rows": [
    {
      "cells": [
        { "text": { "text": "Product" }, "is_header": true, "align": "left" },
        { "text": { "text": "Stock" }, "is_header": true, "align": "center" },
        { "text": { "text": "Price" }, "is_header": true, "align": "right" }
      ]
    },
    {
      "cells": [
        { "text": { "text": "Cloud Server A" }, "align": "left" },
        { "text": { "text": "14" }, "align": "center" },
        { "text": { "text": "$49.00" }, "align": "right" }
      ]
    }
  ]
}
```

### فارسی — خروجی جیسون و نکات مهم
- در حالت ارسال با `blocks`، فیلدهای `has_borders`، `is_striped` و `is_compact` مستقیماً بولین هستند و متن درون سلول‌ها به صورت آبجکت `text` ارسال می‌شود.
- در کلاینت‌های دسکتاپ و موبایل، در صورتی که جدول بیش از حد عریض باشد، به صورت خودکار قابلیت اسکرول افقی فعال می‌شود تا ساختار پیام آسیب نبیند.
- همواره از `compact` برای جدول‌های موبایلی استفاده کنید تا تراکم داده‌ها بهینه باشد.

