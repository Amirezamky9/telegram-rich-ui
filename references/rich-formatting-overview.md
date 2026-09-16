# Rich Formatting Overview (Telegram Bot API 10.3)

Telegram Bot API 10.3 introduces a dedicated rich messaging presentation system (`sendRichMessage`, `editRichMessageText`, `sendRichMessageDraft`) supporting hierarchical block layouts, inline buttons, LaTeX mathematics, localized timestamps, expandable quotes, and native tables.

## Bot API 10.3 Additions

The 10.3 release finalizes and unifies structured message presentation:
- **`sendRichMessage`**: Primary method for delivering structured rich messages with block layouts.
- **`editRichMessageText`**: Method for updating existing messages with a new `rich_message` structure.
- **`RichMessageButton` / `RichTextButton`**: Native button entities flowing directly within paragraph text.
- **`RichBlockButtons` / `InputRichBlockButtons`**: Dedicated container blocks grouping buttons into aligned rows (`left`, `center`, `right`).
- **`RichBlockDocument` / `InputRichBlockDocument`**: Embedded document attachments referenced via `tg://document?id=`.
- **`EphemeralMessageParameters`**: Unified parameter object replacing legacy `receiver_user_id` and `callback_query_id` across send/edit methods.
- **`sendRichMessageDraft`**: Streaming draft interface with `can_stop` and `keep_on_stop` parameters for responsive real-time generation.

### فارسی — قابلیت‌های نسخه ۱۰.۳
نسخه ۱۰.۳ تلگرام ساختار پیام‌های ریچ را کامل کرده است:
- ارسال پیام با ساختار بلوکی از طریق متد `sendRichMessage`.
- دکمه‌های ریچ درون متن (`RichTextButton`) و ردیف دکمه‌ها (`RichBlockButtons`).
- نقل‌قول‌های جمع‌شونده (`<blockquote expandable>`) و جدول‌های فشرده (`compact`).
- الصاق اسناد با لینک‌های اختصاصی `tg://document?id=`.
- پیام‌های موقت و خصوصی گروهی با ساختار یکپارچه `EphemeralMessageParameters`.
- استریم و تولید گام‌به‌گام پیش‌نویس با `sendRichMessageDraft`.

---

## API Methods & Parameter Specification

### `sendRichMessage`

Sends a rich message to a specified chat.

| Field | Type | Required | Description |
|:---|:---|:---|:---|
| `chat_id` | `Integer` or `String` | Yes | Target chat ID or `@channelusername`. |
| `rich_message` | `InputRichMessage` | Yes | Object containing `html`, `markdown`, or `blocks`. |
| `message_thread_id` | `Integer` | Optional | Unique identifier for the target message thread (forum topics). |
| `disable_notification` | `Boolean` | Optional | Sends the message silently without notification sound. |
| `protect_content` | `Boolean` | Optional | Protects content from forwarding and saving. |
| `ephemeral_message_parameters` | `EphemeralMessageParameters` | Optional | Delivers the message as user-private ephemeral in groups. |
| `reply_parameters` | `ReplyParameters` | Optional | Reply configuration targeting existing message or ephemeral message. |
| `reply_markup` | `InlineKeyboardMarkup` | Optional | Additional inline keyboard attached below the message. |

### `rich_message` Object Schema

The `rich_message` object accepts **exactly one** content payload:

| Field | Type | Description |
|:---|:---|:---|
| `html` | `String` | Rich HTML formatted string (1–32,768 characters). |
| `markdown` | `String` | Rich Markdown formatted string (1–32,768 characters). |
| `blocks` | `Array of InputRichBlock` | Array of structured JSON block objects. |
| `is_rtl` | `Boolean` | Optional. Explicit text direction (`true` for RTL, `false` for LTR). |

### `editRichMessageText`

Edits an existing rich message text or layout.

| Field | Type | Required | Description |
|:---|:---|:---|:---|
| `chat_id` | `Integer` or `String` | Optional | Required if `inline_message_id` is not specified. |
| `message_id` | `Integer` | Optional | Required if `inline_message_id` is not specified. |
| `inline_message_id` | `String` | Optional | Required if `chat_id` and `message_id` are not specified. |
| `rich_message` | `InputRichMessage` | Yes | Replacement rich message structure. |
| `reply_markup` | `InlineKeyboardMarkup` | Optional | Replacement inline keyboard markup. |

### `sendRichMessageDraft`

Streams text and structural updates for ongoing generation (e.g. AI bot responses).

| Field | Type | Required | Description |
|:---|:---|:---|:---|
| `chat_id` | `Integer` or `String` | Yes | Target chat ID. |
| `draft_id` | `Integer` | Yes | Client-provided unique draft identifier to correlate updates. |
| `rich_message` | `InputRichMessage` | Yes | Current state of generated rich message. |
| `can_stop` | `Boolean` | Optional | Displays a stop-generation button in client UI. |
| `keep_on_stop` | `Boolean` | Optional | Preserves accumulated draft text if user taps stop. |
| `message_thread_id` | `Integer` | Optional | Thread ID for topic chats. |

### فارسی — متدهای API و پارامترها
- همیشه دقیقاً یکی از کلیدهای `html`، `markdown` یا `blocks` باید ارسال شود. ارسال هم‌زمان چند کلید خطای ۴۰۰ ایجاد می‌کند.
- برای زبان‌های فارسی و عربی، فیلد `is_rtl: true` جهت متن را راست‌به‌چپ تثبیت می‌کند؛ در صورت ارسال نشدن، کلاینت با کاراکترهای ابتدایی جهت را حدس می‌زند.
- استریم پیش‌نویس با `draft_id` انجام می‌شود و تلگرام رویداد توقف کاربر را با آپدیت `stopped_message_generation` گزارش می‌دهد.

---

## Rich HTML vs Rich Markdown Parsing Engine

### Parsing Selection

When receiving raw text, parsers distinguish HTML from Markdown using tag detection:

```typescript
function detectRichMode(source: string): 'html' | 'markdown' {
  // If text contains HTML tags like <p>, <b>, <tg-emoji>, parse as HTML
  return /<\/?[a-z][\s\S]*?>/i.test(source) ? 'html' : 'markdown';
}
```

### Migration Path from Legacy `parse_mode`

| Legacy API (`sendMessage`) | Bot API 10.3 (`sendRichMessage`) | Migration Action |
|:---|:---|:---|
| `text: "<b>Hi</b>", parse_mode: "HTML"` | `rich_message: { html: "<p><b>Hi</b></p>" }` | Wrap root paragraphs in `<p>`, change endpoint to `sendRichMessage`. |
| `text: "*Hi*", parse_mode: "MarkdownV2"` | `rich_message: { markdown: "**Hi**" }` | Adopt standard CommonMark bold/italic; stop backslash-escaping punctuation. |
| Monospace ASCII tables (`<pre>`) | `<table bordered compact>...</table>` | Convert text grids into native HTML table tags. |
| Bottom-only inline buttons | Inline `<tg-button>` or `<tg-button-row>` | Move contextual buttons directly into paragraph content. |

### فارسی — مهاجرت از parse_mode قدیمی
در نسخه ۱۰.۳ نیازی به اسکیپ کردن کاراکترهای خاص با بک‌اسلش (مانند MarkdownV2) نیست. مارک‌داون ریچ از قواعد استاندارد پیروی کرده و تگ‌های HTML بدون ناسازگاری پارس می‌شوند.

---

## Inline Entity Reference (Complete Coverage)

### 1. Basic Typography: Bold, Italic, Underline, Strikethrough

```html
<!-- HTML Syntax -->
<b>Bold text</b> and <strong>strong emphasis</strong>
<i>Italic text</i> and <em>emphasized voice</em>
<u>Underlined text</u> and <ins>inserted text</ins>
<s>Strikethrough text</s> and <del>deleted text</del>
```

```markdown
<!-- Markdown Syntax -->
**Bold text** or __Bold text__
*Italic text* or _Italic text_
~~Strikethrough text~~
```

> **Rule:** Both `<u>` and `<ins>` underline content. Both `<s>` and `<del>` strike through content.
> 
> *فارسی:* تگ‌های `<b>` و `<strong>` برای متن ضخیم، `<i>` و `<em>` برای ایتالیک، `<u>` و `<ins>` برای زیرخط، و `<s>` و `<del>` برای خط‌خورده هستند.

### 2. Spoilers

Conceals sensitive information until the user clicks or taps to reveal.

```html
<tg-spoiler>Secret verification code: 849201</tg-spoiler>
```

```markdown
||Secret verification code: 849201||
```

> *فارسی:* محتوای بین `<tg-spoiler>` یا `||...||` تا زمان کلیک کاربر تار و مخفی باقی می‌ماند.

### 3. Highlights & Marks

Renders a distinct background highlight behind important text passages.

```html
<mark>Critical system alert: server load exceeds 95%.</mark>
```

```markdown
==Critical system alert: server load exceeds 95%.==
```

> *فارسی:* هایلایت متنی با `<mark>` یا `==متن==` پس‌زمینه رنگی مشخصی برای جلب توجه ایجاد می‌کند.

### 4. Subscript & Superscript

Renders mathematical indices, formulas, or ordinal suffixes above/below the baseline.

```html
Water formula: H<sub>2</sub>O
Einstein equation: E = mc<sup>2</sup>
Mathematical coordinates: x<sub>1</sub>, y<sub>1</sub>
Ordinal ranking: 1<sup>st</sup> place
```

> *فارسی:* تگ `<sub>` متن را زیر خط پایه (مانند فرمول آب H₂O) و `<sup>` بالای خط پایه (توان‌ها و رتبه‌ها) قرار می‌دهد.

### 5. Code and Preformatted Blocks

Inline code wraps short snippets in monospaced font. Multiline preformatted code preserves indentation and displays language badges.

```html
Inline: <code>const status = "active";</code>

Block:
<pre><code class="language-typescript">interface OrderItem {
  id: string;
  qty: number;
  price: number;
}
console.log("Order processed");</code></pre>
```

```markdown
Inline: `const status = "active";`

```typescript
interface OrderItem {
  id: string;
  qty: number;
  price: number;
}
```
```

> *فارسی:* کد تک‌خطی با `<code>` و بلوک چندخطی با `<pre><code class="language-...">` نوشته می‌شود. فاصله‌ها و شکست خط دقیقاً حفظ می‌شوند.

### 6. Quotations, Pull Quotes, and Expandable Blocks

```html
<!-- Standard blockquote -->
<blockquote>A wise decision begins with reliable data.</blockquote>

<!-- Nested blockquote -->
<blockquote>
  Strategy statement.
  <blockquote>Operational clarification inside nested quote.</blockquote>
</blockquote>

<!-- Expandable blockquote (Bot API 10.3) -->
<blockquote expandable>
  Tap to expand long terms and conditions.
  Full legal clauses appear here after expansion.
  Additional compliance requirements and liability disclosures.
</blockquote>

<!-- Pull quote with citation -->
<aside>
  Great interfaces anticipate user intent.
  <cite>UI Design Principles</cite>
</aside>
```

> *فارسی:* ویژگی جدید ۱۰.۳ نقل‌قول بازشونده با تگ `<blockquote expandable>` است که برای متن‌های طولانی و قوانین حقوقی مناسب است تا فضای چت شلوغ نشود. تگ `<aside><cite>` برای نقل‌قول‌های برجسته همراه با ذکر نام گوینده به کار می‌رود.

### 7. Collapsible Disclosures (`<details><summary>`)

Allows hiding supplementary content behind interactive accordion toggles.

```html
<details>
  <summary>Frequently Asked Questions</summary>
  <p>Our bot processes orders within 5 seconds of payment confirmation.</p>
</details>

<details open>
  <summary>System Diagnostics (Open by default)</summary>
  <p>Database: Healthy · Cache: 99.8% hit rate</p>
</details>
```

> *فارسی:* تگ `<details>` محتوای مخفی ایجاد می‌کند که با کلیک روی `<summary>` باز می‌شود. افزودن صفت `open` باعث می‌شود بخش از ابتدا باز باشد.

### 8. Localized Timestamps (`<tg-time>`)

Renders a Unix timestamp formatted automatically in the reader's device timezone and locale.

```html
<tg-time unix="1773660000" format="wDT">Tomorrow at 14:00</tg-time>
```

- `unix`: Integer timestamp in seconds since epoch (UTC).
- `format`: Formatting flags (e.g. `wDT` for weekday + date + time, `D` for date only, `T` for time only).
- The inner text serves as fallback for legacy clients.

> *فارسی:* تگ `<tg-time>` تاریخ و ساعت یونیکس را بر اساس منطقه زمانی و زبان گوشی هر کاربر نمایش می‌دهد؛ متن درون تگ برای کلاینت‌های قدیمی به عنوان جایگزین استفاده می‌شود.

### 9. Mathematical Expressions (`<tg-math>`, `<tg-math-block>`)

Renders LaTeX mathematical equations. In web previews and modern clients, rendered with KaTeX/LaTeX engines.

```html
<!-- Inline LaTeX -->
The distance formula is <tg-math>d = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}</tg-math>.

<!-- Block LaTeX -->
<tg-math-block>
\int_{a}^{b} f(x)\,dx = F(b) - F(a)
</tg-math-block>
```

```markdown
Inline: $\frac{a^2 + b^2}{c}$

Block:
$$
E = mc^2
$$
```

> *فارسی:* فرمول‌های ریاضی به صورت لاتک (LaTeX) نوشته می‌شوند. درون خط با `<tg-math>` یا `$..$` و بلوک مستقل با `<tg-math-block>` یا `$$..$$`.

### 10. Links, Mentions, Anchors, and Footnotes

```html
<!-- Standard external link -->
<a href="https://core.telegram.org/bots/api">Bot API Docs ↗</a>

<!-- Numeric user mention (bypasses username changes) -->
<a href="tg://user?id=777000">Telegram Service Notifications</a>

<!-- Intra-message named anchor -->
<a name="section-billing"></a>
<h3>Billing Information</h3>

<!-- Intra-message anchor jump link -->
<p><a href="#section-billing">Jump to Billing ↑</a></p>
```

#### Footnotes in Rich Markdown

```markdown
High-throughput transactions require persistent ledger guarantees[^consensus].

[^consensus]: Raft or PBFT protocol ensures distributed consensus across cluster nodes.
```

> *فارسی:* پیوند با شناسه عددی (`tg://user?id=...`) بدون وابستگی به یوزرنیم کاربر عمل می‌کند. پیوند لنگر (`#anchor`) امکان پرش داخل متن همان پیام را فراهم می‌سازد. پاورقی‌ها در مارک‌داون با `[^id]` و تعریف با `[^id]: متن` ساخته می‌شوند.

---

## Auto Entity Detection & Configuration

By default, Telegram detects recognizable patterns:
- **Email:** `contact@example.com`
- **Phone Number:** `+1 202 555 0123`
- **Bank Card Number:** `4111 1111 1111 1111` (renders with copy/action sheet in client)
- **User Mentions:** `@username`
- **Hashtags:** `#TeleRich`
- **Cashtags:** `$TON`, `$BTC`

### Disabling Link Previews and Detection

To prevent automatic link preview bubbles from dominating the UI when sending rich URLs, pass `link_preview_options`:

```json
{
  "chat_id": 123456789,
  "rich_message": {
    "html": "<p>Visit our platform at <a href=\"https://example.com\">example.com</a></p>"
  },
  "link_preview_options": {
    "is_disabled": true
  }
}
```

To prevent phone numbers or card numbers from rendering interactive sheets when writing test/dummy data, wrap characters in non-breaking spaces or format as inline code `<code>4111 ...</code>`.

### فارسی — تشخیص خودکار موجودیت‌ها
تلگرام به‌طور پیش‌فرض ایمیل، شماره تلفن، کارت بانکی، یوزرنیم و هشتگ را شناسایی می‌کند. برای جلوگیری از باز شدن کادر پیش‌نمایش لینک در پایین پیام، همیشه `link_preview_options: { is_disabled: true }` را همراه درخواست ارسال کنید.

