# Rich Buttons and Colors (Telegram Bot API 10.3)

Telegram Bot API 10.3 introduces native rich interactive buttons embedded directly within message documents. Unlike legacy inline keyboards that attach strictly below the message bubble as `reply_markup`, Bot API 10.3 supports buttons placed inline within running paragraph text (`RichTextButton`) as well as dedicated row-grouped containers (`RichBlockButtons`).

In addition to traditional URLs and callback actions, rich buttons support clipboard copying (`copy_text`), granular inline-query targeting (`switch_inline_query_chosen_chat`), and semantic color styles (`primary`, `success`, `danger`, `link`).

### فارسی — دکمه‌های ریچ و رنگ‌ها در نسخه ۱۰.۳
در نسخه ۱۰.۳ تلگرام، دکمه‌ها می‌توانند مستقیماً درون متن پیام یا در ردیف‌های اختصاصی زیر متن قرار گیرند:
- **دکمه درون‌خطی (Inline):** داخل تگ `<p>` در کنار کلمات و ایموجی‌ها جریان دارد.
- **ردیف دکمه (Row-grouped):** با `<tg-button-row>` در ردیف‌های منظم با تراز چپ، وسط یا راست چیده می‌شود.
- **رنگ‌های معنایی:** رنگ‌های `primary` (آبی)، `success` (سبز)، `danger` (قرمز) و `link` (پیوند ظریف). رنگ‌های دلخواه هگز (Hex) پشتیبانی نمی‌شوند و تم تلگرام اعمال می‌شود.
- **اقدامات جدید:** کپی متن در کلیپ‌بورد با `copy_text`، باز کردن مینی‌اپ با `web_app`، و وضعیت غیرفعال با `disabled`.

---

## Dual Placement Modes

Rich buttons provide two distinct layout paradigms. Both modes accept all action types and styles.

```html
<!-- Mode 1: Inline Flow inside a paragraph -->
<p>
  Need assistance? Contact our
  <tg-button type="url" style="primary" url="https://t.me/SupportBot">Support</tg-button>
  team or tap
  <tg-button type="copy_text" text="/help">Copy /help</tg-button>
  for quick commands.
</p>

<!-- Mode 2: Row-Grouped Containers -->
<tg-button-row align="center">
  <tg-button type="url" style="success" url="https://t.me">Explore TeleRich ↗</tg-button>
  <tg-button type="callback_data" style="primary" data="cart:checkout">Checkout</tg-button>
</tg-button-row>
<tg-button-row align="right">
  <tg-button type="disabled">Out of Stock</tg-button>
</tg-button-row>
```

### 1. In-Text Flowing Buttons (`<tg-button>`)
When placed directly inside `<p>`, `<li>`, or `<blockquote>`, the button flows alongside text entities, custom emojis, and localized timestamps. It occupies inline layout space and wraps naturally with adjacent words.

### 2. Grouped Row Placement (`<tg-button-row>`)
When placed as a top-level block inside `<tg-button-row>`, buttons form a dedicated button bar. The container controls horizontal alignment via the `align` attribute:
- `align="left"` (default): Rows pack from left to right.
- `align="center"`: Rows center horizontally within the bubble.
- `align="right"`: Rows align to the right margin.

### فارسی — تفاوت دو شیوه چیدمان
- **درون‌خطی (`<tg-button>` داخل `<p>`):** دکمه مثل یک کلمه درون جمله می‌نشیند. مناسب برای لینک‌های ارجاعی، دکمه‌های کپی سریع کد رهگیری یا لایسنس در متن.
- **بلوک ردیفی (`<tg-button-row>`):** دکمه‌ها را به صورت ردیف‌های منظم افقی دسته‌بندی می‌کند. با ویژگی `align` می‌توان چیدمان را روی `left`، `center` یا `right` تنظیم کرد. مناسب برای گزینه‌های انتخابی فرم‌ها، منوها و دکمه‌های اصلی پرداخت و خرید.

---

## Attribute Matrix & Action Types

Each button type uses a specific attribute to carry its operational payload. Supplying payload data in the wrong attribute results in parser rejection or unclickable controls.

| Action Type (`type=`) | Payload Attribute | Allowed Color Styles | Chat Restrictions | Description |
|:---|:---|:---|:---|:---|
| `url` | `url="..."` | `primary`, `success`, `danger` | All chats, channels | Opens an external HTTPS link or `tg://` protocol link. |
| `callback_data` | `data="..."` | `primary`, `success`, `danger`, `link` | Private, groups, supergroups | Emits a `CallbackQuery` containing 1–64 UTF-8 bytes. |
| `web_app` | `url="..."` | `primary`, `success`, `danger` | **Private chats only** | Launches a Telegram Mini App with `initData` authentication. |
| `switch_inline_query` | `query="..."` | `primary`, `success`, `danger` | All chats | Prompts user to select a chat and inserts bot username + query. |
| `switch_inline_query_current_chat` | `query="..."` | `primary`, `success`, `danger` | Private, groups | Inserts bot username + query directly in the current chat. |
| `switch_inline_query_chosen_chat` | `query="..."` + flags | `primary`, `success`, `danger` | All chats | Filters target chat types when prompting user for inline query. |
| `copy_text` | `text="..."` | `primary`, `success`, `danger` | All chats, channels | Copies literal string (1–256 chars) to system clipboard. |
| `disabled` | *(none)* | `primary`, `success`, `danger`, *(default)* | All chats, channels | Renders unclickable disabled button displaying muted text. |

### Detailed Action Semantics

#### 1. External URL (`type="url"`)
```html
<tg-button type="url" style="primary" url="https://telegram.org">Telegram Website ↗</tg-button>
<tg-button type="url" url="tg://user?id=777000">Support Representative</tg-button>
```
Carries target URL in `url`. Accepts standard `https://` destinations and supported Telegram internal schemes (`tg://user?id=...`, `tg://resolve?domain=...`).

#### 2. Callback Data (`type="callback_data"`)
```html
<tg-button type="callback_data" style="success" data="order:confirm:9482">Confirm Order</tg-button>
<tg-button type="callback_data" style="link" data="order:details">View Details</tg-button>
```
Carries callback payload in `data`. The payload must not exceed 64 UTF-8 bytes. Supports nested rich markup inside button label text (e.g. `<tg-emoji>` or `<tg-time>`).

#### 3. Telegram Mini App (`type="web_app"`)
```html
<tg-button type="web_app" style="success" url="https://app.example.com/checkout">Open Store</tg-button>
```
Opens the configured web application. **Chat restriction:** Telegram Bot API restricts `web_app` buttons to private chats between the user and the bot. Using `web_app` in channels or groups will fail client validation.

#### 4. Inline Query Switching (`switch_inline_query*`)
```html
<!-- Switch to any chat -->
<tg-button type="switch_inline_query" query="search term">Share Product</tg-button>

<!-- Switch in current chat -->
<tg-button type="switch_inline_query_current_chat" query="filter:active">Filter Active</tg-button>

<!-- Switch with target chat type filtering -->
<tg-button type="switch_inline_query_chosen_chat"
           query="share:invite"
           allow-user-chats
           allow-group-chats
           allow-channel-chats>Share with Group or Channel</tg-button>
```
The `switch_inline_query_chosen_chat` type supports four boolean flags to constrain chat picker selection:
- `allow-user-chats`: Permit individual private user chats.
- `allow-bot-chats`: Permit chats with other bots.
- `allow-group-chats`: Permit basic groups and supergroups.
- `allow-channel-chats`: Permit broadcast channels.

#### 5. Clipboard Copy (`type="copy_text"`)
```html
<tg-button type="copy_text" text="TR-2026-X992">Copy Tracking Code</tg-button>
```
Carries string to copy in `text`. When tapped, Telegram client immediately copies the string to the operating system clipboard and flashes a confirmation toast notification.

#### 6. Disabled Button (`type="disabled"`)
```html
<tg-button type="disabled">Sold Out</tg-button>
<tg-button type="disabled" style="danger">Booking Closed</tg-button>
```
Renders an unclickable button with muted typography and disabled interaction states. Useful for preserving grid positions in dynamic booking matrices without triggering empty callbacks.

---

## Color Styles & Theme Integration

Bot API 10.3 establishes semantic button color palettes linked directly to the client's active Telegram theme:

| Style (`style=`) | Visual Presentation | Supported Types | Semantics & Recommended Use |
|:---|:---|:---|:---|
| `primary` | Telegram Accent Blue | All types | Primary submission, affirmative progression, highlighted calls-to-action. |
| `success` | Vibrant Theme Green | All types | Payment approvals, order confirmation, cart checkout, status completions. |
| `danger` | Vivid Alert Red | All types | Cancellation, order rejection, deletion, destructive account actions. |
| `link` | Subtle borderless link text | `callback_data` only | Secondary actions, dismissals, footer navigations, expanded disclosures. |
| *(omitted)* | Default surface button | All types | Neutral actions, secondary navigation, standard options. |

> **Critical Styling Rule:** Button styles adapt dynamically to dark mode, light mode, and custom Telegram user themes. **Arbitrary CSS colors or hex codes (e.g. `#ff0000`) are strictly rejected by the Bot API parser.** Only the standard semantic identifiers (`primary`, `success`, `danger`, `link`) are valid.

### فارسی — استایل‌ها و محدودیت رنگ‌ها
- رنگ دکمه‌ها از تم کاربر (حالت تیره/روشن تلگرام) تبعیت می‌کند.
- تلگرام کدهای هگز دلخواه مثل `#ff5500` را نمی‌پذیرد. فقط چهار شناسه مجازند: `primary` (آبی اصلی)، `success` (سبز تایید)، `danger` (قرمز هشدار)، و `link` (لینک بدون کادر).
- استایل `link` منحصراً برای دکمه‌های نوع `callback_data` مجاز است.

---

## Rich Buttons vs `reply_markup` Inline Keyboards

Telegram now supports two parallel button architectures. They can be used independently or combined within the same message.

| Dimension | Rich Buttons (`<tg-button>`, `<tg-button-row>`) | Legacy `reply_markup` (`InlineKeyboardMarkup`) |
|:---|:---|:---|
| **Placement** | Embedded inside the message text or immediately below text blocks | Anchored strictly outside and below the entire message bubble |
| **Inline Flow** | Yes. Can flow inline inside sentences alongside text and entities | No. Strictly arranged in a separated 2D rectangular grid |
| **Layout Control** | Paragraph flow or horizontal block rows (`align="left/center/right"`) | Fixed multi-row grid of buttons spanning bubble width |
| **Editability** | Edited atomically with the message text via `editRichMessageText` | Can be edited independently without re-sending or modifying text |
| **Callback Limits** | Max 64 UTF-8 bytes in `data="..."` | Max 64 UTF-8 bytes in `callback_data` |
| **Custom Emoji Icons** | Yes: embed `<tg-emoji>` directly inside button text content | Yes: specify `icon_custom_emoji_id` on `InlineKeyboardButton` (API 9.4+) |
| **Legacy Client Behavior** | Degrades to attached keyboard rows below bubble or plain text links | Fully supported on all legacy Telegram clients across platforms |

### Architecture Decision: Which to Use?
- **Use Rich Buttons when:**
  - The button is contextually tied to a specific paragraph (e.g. "Copy license key: `<tg-button type="copy_text" ...>`").
  - Designing branded e-commerce product cards with aligned `success` checkout buttons and `primary` options.
  - You need inline buttons inside lists, tables, or expandable blockquotes.
- **Use `reply_markup` Keyboards when:**
  - Building persistent bottom navigation menus or keyboards that need to be edited independently while keeping message text static.
  - Supporting outdated third-party Telegram clients that lack Bot API 10.3 block rendering.
- **Combining Both:**
  - A message can include inline rich buttons within its body (e.g. a "Copy Tracking Number" button) while attaching a global `reply_markup` keyboard below (e.g. `[ Back to Main Menu ]`).

---

## `RichBlockButtons` JSON Schema

When sending structured JSON blocks (`rich_message.blocks`) instead of HTML, button rows are compiled into `InputRichBlockButtons`:

```json
{
  "type": "buttons",
  "align": "center",
  "buttons": [
    {
      "text": "Buy Now ($49)",
      "type": "url",
      "style": "success",
      "url": "https://store.example.com/item/101"
    },
    {
      "text": "Copy SKU",
      "type": "copy_text",
      "style": "primary",
      "copy_text": "SKU-PROD-998"
    },
    {
      "text": "Reviews",
      "type": "callback_data",
      "style": "link",
      "data": "reviews:item:101"
    }
  ]
}
```

### فارسی — ساختار بلوکی دکمه‌ها
در صورتی که از فرمت JSON بلوکی (`blocks`) استفاده شود، هر ردیف دکمه با شیء `InputRichBlockButtons` تعریف می‌شود که فیلد `align` تراز ردیف و آرایه `buttons` مشخصات هر دکمه را تعیین می‌کند.

---

## Callback Handling & In-Place Editing

Handling rich button callbacks follows the standard Telegram Bot API callback contract with specific rich message considerations:

```python
# 1. Acknowledge the callback immediately (prevents client spinner timeout)
await bot.answer_callback_query(
    callback_query_id=query.id,
    text="Processing request...",
    show_alert=False
)

# 2. Update the rich message in-place with new layout or state
await bot.edit_rich_message_text(
    chat_id=query.message.chat.id,
    message_id=query.message.message_id,
    rich_message={
        "html": "<p>Order <b>#9482</b> Status: <i>Paid</i></p>"
                "<tg-button-row align='center'>"
                "  <tg-button type='callback_data' style='primary' data='order:track:9482'>Track Delivery</tg-button>"
                "</tg-button-row>"
    }
)
```

### Callback Invariants
1. **Immediate Acknowledgment:** Always call `answerCallbackQuery` within 30 seconds to dismiss the client loading animation.
2. **Payload Size Guard:** Keep `data` under 64 UTF-8 bytes. For complex state, pass an identifier (e.g. `order:9482:item:3`) and look up details in Redis/KV.
3. **In-Place Updates:** Use `editRichMessageText` (or `editMessageText` with `rich_message`) to avoid polluting the chat with new messages upon every button click.

### فارسی — مدیریت کال‌بک و ویرایش پیام
۱. پاسخ فوری با `answerCallbackQuery` برای متوقف کردن لودینگ کلاینت الزامی است (حداکثر ۳۰ ثانیه).
۲. محدودیت ۶۴ بایت داده در فیلد `data` پابرجاست؛ شناسه‌ها را کوتاه انتخاب کنید و داده‌های سنگین را در دیتابیس نگه دارید.
۳. برای به‌روزرسانی محتوای پیام پس از کلیک دکمه، از `editRichMessageText` استفاده کنید تا دکمه‌ها و متن به صورت یکپارچه ویرایش شوند.

---

## Edge Cases, Security & Troubleshooting

### Forbidden Entity Nesting
Telegram Bot API strictly enforces that interactive entities cannot be nested within one another:
- **Forbidden:** `<a href="...">...<tg-button>...</tg-button>...</a>` (button inside a link).
- **Forbidden:** `<tg-button type="url" ...><a href="...">...</a></tg-button>` (link inside a button).
- **Forbidden:** `<tg-button ...><tg-button ...>...</tg-button></tg-button>` (nested buttons).
- **Allowed:** Nesting styling entities inside buttons, such as `<b>`, `<i>`, `<tg-emoji>`, and `<tg-time>`.

### Common Error Codes

| Error Signature | Root Cause | Resolution |
|:---|:---|:---|
| `BUTTON_DATA_INVALID` | `data` attribute exceeds 64 UTF-8 bytes | Shorten callback key or encode state as an ID. |
| `BUTTON_TYPE_INVALID` | Unrecognized value in `type="..."` | Ensure `type` is one of the 8 supported action strings. |
| `BUTTON_STYLE_INVALID` | Invalid `style="..."` or hex color used | Use only `primary`, `success`, `danger`, or `link`. |
| `WEB_APP_NOT_ALLOWED` | `type="web_app"` button sent to channel or group | Restrict Mini App buttons to 1-on-1 private bot chats. |
| `RICH_MESSAGE_TOO_LONG` | Compiled message exceeds 32,768 characters | Paginate items or deliver full catalog as an external link. |

### فارسی — خطاهای رایج دکمه‌ها
- قرار دادن تگ‌های تعاملی داخل یکدیگر (مانند لینک داخل دکمه یا دکمه داخل لینک) باعث رد پیام توسط تلگرام می‌شود.
- استفاده از مینی‌اپ در کانال یا گروه با خطای `WEB_APP_NOT_ALLOWED` متوقف می‌شود؛ این دکمه‌ها فقط در چت خصوصی ربات مجاز هستند.


