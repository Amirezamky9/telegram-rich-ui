# Custom Emojis and Stickers (Telegram Bot API 10.3)

Telegram allows bots to embed custom animated and vector emojis within message text and interactive keyboard buttons. Custom emojis transform bot interfaces from generic plain text into branded, high-polish application experiences.

---

## `<tg-emoji>` Syntax & Fundamentals

In Telegram Bot API HTML parsing (both legacy and `sendRichMessage`), custom emojis are defined using the `<tg-emoji>` tag:

```html
<p>
  Welcome to our platform!
  <tg-emoji emoji-id="5368324170671202286">👍</tg-emoji>
  Your verification badge is ready:
  <tg-emoji emoji-id="5465465412345678901">⭐</tg-emoji>
</p>
```

### Tag Attributes and Content

| Component | Role | Requirement |
|:---|:---|:---|
| `emoji-id` | The unique 64-bit integer identifier (passed as a string) corresponding to the Telegram custom emoji sticker document. | **Required** |
| Inner Text (`👍`) | The unicode character rendered as fallback whenever custom emojis cannot be loaded or are not supported by the client. | **Required** |

### Critical Rules
1. **Never leave the inner text empty:** Writing `<tg-emoji emoji-id="..."></tg-emoji>` results in invisible blank gaps on older clients, web versions, or notification banners.
2. **Never self-close:** Always write opening `<tg-emoji>` and closing `</tg-emoji>` tags. Self-closing `<tg-emoji ... />` breaks HTML document trees.
3. **Valid String Representation:** Always pass `emoji-id` as a string of digits (e.g. `"5368324170671202286"`), as 64-bit integers exceed standard JavaScript safe integer precision (`Number.MAX_SAFE_INTEGER`).

### فارسی — ساختار ایموجی‌های سفارشی
- تگ `<tg-emoji emoji-id="...">👍</tg-emoji>` برای نمایش ایموجی‌های سفارشی انیمیشنی یا وکتور به کار می‌رود.
- صفت `emoji-id` شناسه عددی ۶۴ بیتی است که باید حتماً به صورت رشته (String) ارسال شود تا در جاوااسکریپت دقت عددی آن آسیب نبیند.
- متن داخل تگ (مانند `👍`) **کاراکتر جایگزین (Fallback)** است. اگر اینترنت ضعیف باشد، نسخه تلگرام قدیمی باشد، یا در بخش نوتیفیکیشن گوشی، این کاراکتر یونیکد نمایش داده می‌شود؛ بنابراین این بخش هرگز نباید خالی رها شود.

---

## The Telegram Premium Requirement for Bots

Custom emojis are a Telegram Premium ecosystem feature. However, **bots cannot subscribe to Telegram Premium directly**. Instead, Telegram enforces an ownership linkage:

### The Owner Prerequisite Rule

> **Rule:** For a bot to send custom emojis to regular (non-Premium) users without restriction, the **personal Telegram account of the bot owner** (the account that originally generated the bot token in `@BotFather`) must maintain an **active Telegram Premium subscription**.

### Operational Consequences

| Scenario | Result in Chat |
|:---|:---|
| **Bot owner has Telegram Premium** | The bot renders custom animated emojis for **all** users, including free users, across private chats, groups, and channels. |
| **Bot owner DOES NOT have Premium** | The bot's custom emojis are stripped or automatically downgraded to their unicode fallback character (`👍`) for non-Premium recipients. |
| **Bot owner Premium expires** | Existing messages retain their rendered assets, but new outgoing messages immediately downgrade to fallback characters. |

### Verifying Bot Capabilities via API

You can verify whether your bot is authorized to post custom emojis by checking your bot profile and testing a test message payload:

```bash
# Verify basic bot identity
curl -s "https://api.telegram.org/bot$BOT_TOKEN/getMe" | jq .
```

### فارسی — شرط تلگرام پرمیوم برای ربات‌ها
- ربات‌ها به خودی خود نمی‌توانند اشتراک پرمیوم خریداری کنند.
- **قانون اصلی:** اکانت شخصی کاربری که ربات را در `@BotFather` ساخته است (مالک ربات) باید **اشتراک فعال تلگرام پرمیوم (Telegram Premium)** داشته باشد.
- اگر مالک ربات پرمیوم داشته باشد، تمام کاربران عادی (حتی بدون پرمیوم) ایموجی‌های سفارشی ارسالی ربات را مشاهده می‌کنند.
- در صورت نداشتن اشتراک پرمیوم توسط سازنده ربات، ایموجی‌ها به کاراکتر یونیکد معمولی داخل تگ (Fallback) تبدیل می‌شوند.

---

## Discovering and Resolving Custom Emoji IDs

Custom emojis originate from custom sticker packs created through Telegram's official `@Stickers` bot. Because Telegram's public web catalogs do not display internal 64-bit entity IDs, developers use dedicated discovery techniques:

### Discovery Techniques

1. **Telegram Updates via `@ShowJsonBot`:**
   - Add the desired custom emoji into a message in Telegram.
   - Forward that message to `@ShowJsonBot` or your own test bot logging updates.
   - Inspect the `entities` array:
     ```json
     {
       "type": "custom_emoji",
       "offset": 0,
       "length": 2,
       "custom_emoji_id": "5368324170671202286"
     }
     ```
2. **`getCustomEmojiStickers` Bot API Method:**
   Call the official Bot API endpoint to inspect and validate known custom emoji IDs:
   ```bash
   curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/getCustomEmojiStickers" \
     -H "Content-Type: application/json" \
     -d '{"custom_emoji_ids": ["5368324170671202286"]}' | jq .
   ```
   Telegram returns a `Sticker` object with pack details, dimensions, thumbnail, and file identifier. Accepts up to 200 IDs per request.

### فارسی — دریافت و بررسی شناسه‌های ایموجی
- شناسه‌های عددی ایموجی را می‌توانید با فوروارد کردن یک پیام حاوی آن ایموجی به ربات‌هایی مثل `@ShowJsonBot` از فیلد `custom_emoji_id` استخراج کنید.
- با متد رسمی `getCustomEmojiStickers` می‌توانید تا ۲۰۰ شناسه ایموجی را در یک درخواست اعتبارسنجی کنید و اطلاعات پک و فایل آن را بگیرید.

---

## Button Icons via `icon_custom_emoji_id`

Telegram Bot API 7.0+ introduced the ability to attach custom animated emojis as dedicated icons on keyboard buttons, both for attached inline keyboards and regular reply keyboards.

### 1. `InlineKeyboardButton` with Custom Emoji Icon

```json
{
  "reply_markup": {
    "inline_keyboard": [
      [
        {
          "text": "Premium Dashboard",
          "url": "https://app.example.com",
          "icon_custom_emoji_id": "5368324170671202286",
          "style": "primary"
        }
      ],
      [
        {
          "text": "Verify Account",
          "callback_data": "action:verify",
          "icon_custom_emoji_id": "5465465412345678901",
          "style": "success"
        },
        {
          "text": "Cancel Order",
          "callback_data": "action:cancel",
          "icon_custom_emoji_id": "5368324170671202299",
          "style": "danger"
        }
      ]
    ]
  }
}
```

### 2. `KeyboardButton` (Reply Keyboard) with Custom Emoji Icon

```json
{
  "reply_markup": {
    "keyboard": [
      [
        {
          "text": "My Orders",
          "icon_custom_emoji_id": "5368324170671202286"
        },
        {
          "text": "Support Center",
          "icon_custom_emoji_id": "5465465412345678901"
        }
      ]
    ],
    "resize_keyboard": true
  }
}
```

### In-Text Rich Buttons with Custom Emoji

In Bot API 10.3, rich buttons placed inside paragraphs (`<tg-button>`) can also contain `<tg-emoji>` directly in their label:

```html
<tg-button-row align="center">
  <tg-button type="callback_data" style="link" data="upvote">
    Like <tg-emoji emoji-id="5368324170671202286">👍</tg-emoji>
  </tg-button>
</tg-button-row>
```

### فارسی — آیکون ایموجی در دکمه‌ها
- از نسخه ۷.۰ به بعد، فیلد `icon_custom_emoji_id` روی دکمه‌های اینلاین (`InlineKeyboardButton`) و دکمه‌های معمولی کیبورد (`KeyboardButton`) پشتیبانی می‌شود.
- در دکمه‌های ریچ درون متن (`<tg-button>`) نیز می‌توان مستقیماً تگ `<tg-emoji>` را داخل برچسب دکمه قرار داد تا آیکون دلخواه کنار متن نمایش داده شود.

---

## Fallback Strategy for Legacy Clients

Outdated Telegram clients and third-party wrappers cannot render custom emojis. To ensure accessibility and graceful degradation:

### Fallback Best Practices

1. **Semantic Alignment:** Always pair the custom emoji with an exact semantic equivalent (e.g. use `⭐` for star badges, `🔔` for alerts, `🛡️` for security).
2. **Never Rely on Emoji Text as Words:** Never replace critical textual words with an emoji without text accompaniment. Instead of `"Click <tg-emoji ...>🛒</tg-emoji> now"`, write `"Click the Cart button <tg-emoji ...>🛒</tg-emoji>"`.
3. **Directional Sensitivity:** In RTL languages (Persian/Arabic), custom emojis inherit the text flow of their immediate surrounding text.

### Brand Asset Registry Pattern

Maintain a centralized dictionary of verified custom emoji IDs to prevent hardcoded magic strings:

```typescript
// assets/emojis.ts
export interface BrandEmoji {
  id: string;
  fallback: string;
  description: string;
}

export const BRAND_EMOJIS = {
  VERIFIED_BADGE: {
    id: '5465465412345678901',
    fallback: '⭐',
    description: 'Verified partner blue star'
  },
  THUMBS_UP: {
    id: '5368324170671202286',
    fallback: '👍',
    description: 'Animated thumbs up reaction'
  },
  SECURITY_SHIELD: {
    id: '5368324170671202299',
    fallback: '🛡️',
    description: 'Active protection shield'
  }
} as const;

export function renderEmoji(emoji: BrandEmoji): string {
  return `<tg-emoji emoji-id="${emoji.id}">${emoji.fallback}</tg-emoji>`;
}
```

### Usage in Messages

```typescript
const messageHtml = `
<p>
  Account Status: ${renderEmoji(BRAND_EMOJIS.VERIFIED_BADGE)} <b>Enterprise Verified</b><br/>
  Security Level: ${renderEmoji(BRAND_EMOJIS.SECURITY_SHIELD)} Maximum Protection
</p>
`;
```

---

## Verification & Troubleshooting Checklist

1. **Check Owner Premium:** If custom emojis fail to show up in test chats, verify that the account in `@BotFather` that created the bot has Telegram Premium.
2. **Validate String Type for IDs:** Ensure IDs are quoted strings (`"5368..."`) in JSON and HTML attributes. Numeric literals in JSON may lose accuracy.
3. **Inspect Raw Chat Output:** Send a test payload to a private chat with a non-Premium account to ensure the fallback character renders cleanly without syntax artifacts.

