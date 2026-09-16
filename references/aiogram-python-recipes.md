# aiogram 3.30+ Python Recipes (Telegram Bot API 10.3)

This guide provides production-ready Python recipes for constructing and dispatching Bot API 10.3 rich messages using `aiogram 3.30+`. It covers typed methods, custom method fallbacks, safe HTML builders, callback routers, ephemeral messaging, and graceful error degradation.

---

## Compatibility Strategy: Native vs Custom Method Fallback

Because Telegram Bot API 10.3 rich methods (`sendRichMessage`, `editRichMessageText`, `sendRichMessageDraft`) may not yet be typed in older point releases of aiogram 3.x, two implementation paths are available.

> **Unverified against a specific aiogram release:** Native method signatures depend on your installed aiogram version. To verify whether your installed aiogram natively types `SendRichMessage`:
> ```bash
> python3 -c "import aiogram.methods; print('Native support:', hasattr(aiogram.methods, 'SendRichMessage'))"
> # Or inspect installed methods:
> python3 -m pip show aiogram
> python3 -c "import aiogram.methods; print([m for m in dir(aiogram.methods) if 'rich' in m.lower()])"
> ```

### Path A: Native aiogram 3.x Method (When Typed)
When running an aiogram release containing Bot API 10.3 types:
```python
from aiogram import Bot
from aiogram.types import Message

# Native call via bot wrapper
async def send_native(bot: Bot, chat_id: int | str, html: str) -> Message:
    return await bot.send_rich_message(
        chat_id=chat_id,
        rich_message={"html": html}
    )
```

### Path B: Generic Custom TelegramMethod (Universal Fallback)
When `sendRichMessage` is not yet packaged in `aiogram.methods`, define a custom `TelegramMethod` using aiogram's extensible RPC engine. This works on any aiogram 3.x release:

```python
from typing import Any, Optional
from aiogram.methods.base import TelegramMethod
from aiogram.types import Message, ReplyParameters, InlineKeyboardMarkup

class SendRichMessage(TelegramMethod[Message]):
    __returning__ = Message
    __api_method__ = "sendRichMessage"

    chat_id: int | str
    rich_message: dict[str, Any]
    message_thread_id: Optional[int] = None
    disable_notification: Optional[bool] = None
    protect_content: Optional[bool] = None
    ephemeral_message_parameters: Optional[dict[str, Any]] = None
    reply_parameters: Optional[ReplyParameters] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None

class EditRichMessageText(TelegramMethod[Message]):
    __returning__ = Message
    __api_method__ = "editMessageText"

    chat_id: Optional[int | str] = None
    message_id: Optional[int] = None
    inline_message_id: Optional[str] = None
    rich_message: dict[str, Any]
    reply_markup: Optional[InlineKeyboardMarkup] = None
```

Calling the custom method:
```python
message = await bot(SendRichMessage(
    chat_id=chat_id,
    rich_message={"html": "<p><b>TeleRich</b> dynamic dispatch.</p>"}
))
```

### فارسی — سازگاری با نسخه‌های مختلف aiogram
اگر پکیج `aiogram` نصب‌شده در محیط شما متد `send_rich_message` را تعریف نکرده باشد، نیازی به ابزار خارجی نیست. با ارث‌بری از `TelegramMethod[Message]` و تعریف `__api_method__ = "sendRichMessage"`، سیستم RPC داخلی aiogram بدون مشکل متد جدید تلگرام را فراخوانی می‌کند.

---

## Safe HTML Builders (Trust Boundary & Escaping)

> **Security Mandate:** Never interpolate raw database records or untrusted user input directly into rich HTML strings. Always sanitize dynamic variables with `html.escape()`. Untrusted `<` or `>` characters break table/button syntax or cause client rendering crashes.

```python
import html
from typing import Any, Optional, Sequence

def safe(val: Any) -> str:
    """Sanitize dynamic values across the trust boundary."""
    return html.escape(str(val) if val is not None else "", quote=True)
```

### 1. Table Builder
Constructs rectangular `<table bordered striped compact>` grids with per-column alignment.

```python
def build_rich_table(
    headers: Sequence[str],
    rows: Sequence[Sequence[Any]],
    alignments: Optional[Sequence[str]] = None,
    bordered: bool = True,
    striped: bool = True,
    compact: bool = True,
    caption: Optional[str] = None,
) -> str:
    attrs = []
    if bordered: attrs.append("bordered")
    if striped: attrs.append("striped")
    if compact: attrs.append("compact")
    attr_str = (" " + " ".join(attrs)) if attrs else ""

    aligns = list(alignments) if alignments else ["left"] * len(headers)
    while len(aligns) < len(headers):
        aligns.append("left")

    parts = [f"<table{attr_str}>"]
    if caption:
        parts.append(f"  <caption>{safe(caption)}</caption>")

    # Header row
    parts.append("  <tr>")
    for h, align in zip(headers, aligns):
        parts.append(f'    <th align="{align}">{safe(h)}</th>')
    parts.append("  </tr>")

    # Data rows
    for row in rows:
        parts.append("  <tr>")
        for cell, align in zip(row, aligns):
            parts.append(f'    <td align="{align}">{safe(cell)}</td>')
        parts.append("  </tr>")

    parts.append("</table>")
    return "\n".join(parts)
```

### 2. Slideshow Carousel Builder
Constructs `<tg-slideshow>` elements combining image URLs and captions.

```python
def build_rich_slideshow(
    media_urls: Sequence[str],
    caption: Optional[str] = None,
    author: Optional[str] = None,
) -> str:
    parts = ["<tg-slideshow>"]
    for url in media_urls:
        parts.append(f'  <img src="{safe(url)}"/>')
    if caption or author:
        parts.append("  <figcaption>")
        if caption:
            parts.append(f"    {safe(caption)}")
        if author:
            parts.append(f"    <cite>{safe(author)}</cite>")
        parts.append("  </figcaption>")
    parts.append("</tg-slideshow>")
    return "\n".join(parts)
```

### 3. Button Row Builder
Constructs aligned `<tg-button-row>` blocks with typed button actions.

```python
def build_rich_button_row(
    buttons: Sequence[dict[str, str]],
    align: str = "left",
) -> str:
    align_attr = f' align="{align}"' if align in ("left", "center", "right") else ""
    parts = [f"<tg-button-row{align_attr}>"]
    for b in buttons:
        b_type = b.get("type", "url")
        label = safe(b.get("label", ""))
        attrs = [f'type="{b_type}"']
        if "style" in b:
            attrs.append(f'style="{b["style"]}"')
        if b_type in ("url", "web_app") and "url" in b:
            attrs.append(f'url="{safe(b["url"])}"')
        elif b_type == "callback_data" and "data" in b:
            attrs.append(f'data="{safe(b["data"])}"')
        elif b_type == "copy_text" and "text" in b:
            attrs.append(f'text="{safe(b["text"])}"')
        elif b_type.startswith("switch_inline_query") and "query" in b:
            attrs.append(f'query="{safe(b["query"])}"')
            for flag in ("allow-user-chats", "allow-bot-chats", "allow-group-chats", "allow-channel-chats"):
                if b.get(flag):
                    attrs.append(flag)

        parts.append(f"  <tg-button {' '.join(attrs)}>{label}</tg-button>")
    parts.append("</tg-button-row>")
    return "\n".join(parts)
```

### فارسی — سازنده‌های HTML و امنیت ورودی
- تمام مقادیر پویا که از دیتابیس یا ورودی کاربر دریافت می‌شوند باید توسط `html.escape` پردازش شوند تا کاراکترهایی مثل `<`، `>` و `&` ساختار پیام ریچ را تخریب نکنند.
- توابع بالا تولید خروجی استاندارد برای جدول (`build_rich_table`)، اسلایدشو (`build_rich_slideshow`) و ردیف دکمه‌ها (`build_rich_button_row`) را به صورت خودکار و امن انجام می‌دهند.

---

## Sending, Editing & Graceful Degradation

In mixed client environments or during server-side transitions, sending a rich message may raise `TelegramBadRequest` if the Bot API version or client rejects the payload. The helper below attempts `sendRichMessage` and falls back cleanly to legacy HTML parsing:

```python
import logging
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)

async def send_rich_or_fallback(
    bot: Bot,
    chat_id: int | str,
    rich_html: str,
    fallback_text: Optional[str] = None,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
) -> Message:
    """Attempts sendRichMessage; falls back to standard sendMessage on failure."""
    try:
        # Try custom method fallback or native call
        return await bot(SendRichMessage(
            chat_id=chat_id,
            rich_message={"html": rich_html},
            reply_markup=reply_markup,
        ))
    except TelegramBadRequest as err:
        logger.warning("Rich message rejected (%s); falling back to legacy HTML.", err.message)
        # Strip unsupported rich tags or deliver sanitized plain fallback
        clean_text = fallback_text or rich_html.replace("<table", "<pre").replace("</table>", "</pre>")
        return await bot.send_message(
            chat_id=chat_id,
            text=clean_text[:4096],
            parse_mode="HTML",
            reply_markup=reply_markup,
        )

async def edit_rich_message_safe(
    bot: Bot,
    chat_id: int | str,
    message_id: int,
    rich_html: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
) -> Message:
    """Edits an existing message in-place with new rich message structure."""
    return await bot(EditRichMessageText(
        chat_id=chat_id,
        message_id=message_id,
        rich_message={"html": rich_html},
        reply_markup=reply_markup,
    ))
```

---

## Router, Callback Queries & Ephemeral Messages

A complete aiogram `Router` demonstrating callback queries, in-place edits, and private ephemeral responses in groups:

```python
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

rich_router = Router(name="rich_ui_router")

@rich_router.message(Command("invoice"))
async def cmd_invoice(message: Message, bot: Bot):
    table = build_rich_table(
        headers=["Item", "Qty", "Price"],
        rows=[
            ["Cloud Server", "1", "$40.00"],
            ["Managed DB", "1", "$25.00"],
        ],
        alignments=["left", "center", "right"],
        caption="Monthly Subscription Invoice",
    )
    buttons = build_rich_button_row([
        {"type": "callback_data", "style": "success", "label": "Pay Now ($65)", "data": "inv:pay:1001"},
        {"type": "copy_text", "label": "Copy Ref", "text": "INV-2026-1001"},
    ], align="center")

    html = f"<h3>Invoice #1001</h3>\n{table}\n{buttons}"
    await send_rich_or_fallback(bot, message.chat.id, html)

@rich_router.callback_query(F.data.startswith("inv:pay:"))
async def handle_payment_callback(query: CallbackQuery, bot: Bot):
    inv_id = query.data.split(":")[2]
    # Always acknowledge within 30s to dismiss spinner
    await query.answer(f"Payment for invoice #{inv_id} received!", show_alert=False)

    # Update rich message in-place
    updated_html = (
        f"<h3>Invoice #{safe(inv_id)}</h3>"
        f"<p>Status: <tg-emoji emoji-id='5368324170671202286'>✅</tg-emoji> <b>Paid in Full</b></p>"
    )
    if query.message:
        await edit_rich_message_safe(
            bot=bot,
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            rich_html=updated_html,
        )

# Ephemeral user-private message in group chat
async def send_group_ephemeral_alert(bot: Bot, chat_id: int, user_id: int, note: str):
    """Sends a message visible strictly to the specified user inside a group chat."""
    html = f"<p>🔒 <b>Private Group Alert:</b> {safe(note)}</p>"
    await bot(SendRichMessage(
        chat_id=chat_id,
        rich_message={"html": html},
        ephemeral_message_parameters={"receiver_user_id": user_id},
    ))
```

### فارسی — مدیریت خطا و پیام‌های موقت
- در صورت بروز خطای `TelegramBadRequest` (مثلاً نسخه کلاینت بسیار قدیمی یا ارور سرور)، تابع `send_rich_or_fallback` به صورت خودکار پیام را به شکل پیام کلاسیک HTML با `parse_mode="HTML"` می‌فرستد تا کاربر پیام را از دست ندهد.
- با تنظیم `ephemeral_message_parameters`، پیام در گروه‌ها منحصراً برای کاربر مشخص‌شده نمایش داده می‌شود و برای سایر اعضا مخفی است.

---

## Runnable Self-Check (No Bot Token Required)

The following runnable verification block tests builder output escaping, table dimensions, and button attributes without making network requests:

```python
if __name__ == "__main__":
    # 1. Test HTML escaping across trust boundary
    malicious_input = '<script>alert("xss")</script> & "quotes"'
    escaped = safe(malicious_input)
    assert "<script>" not in escaped, "Escaping failed to neutralize script tag"
    assert "&lt;script&gt;" in escaped, "Escaping failed to encode brackets"

    # 2. Test table builder structure
    tbl = build_rich_table(
        headers=["Product", "Price"],
        rows=[["Alpha", "$10"], [malicious_input, "$20"]],
        alignments=["left", "right"],
        bordered=True,
        compact=True,
        caption="Pricing & Rates"
    )
    assert "<table bordered striped compact>" in tbl
    assert '<caption>Pricing &amp; Rates</caption>' in tbl
    assert '<td align="right">$10</td>' in tbl
    assert '<script>' not in tbl, "Table builder leaked unescaped input"

    # 3. Test button row builder
    btn_row = build_rich_button_row([
        {"type": "url", "style": "primary", "label": "Shop", "url": "https://t.me"},
        {"type": "copy_text", "label": "Copy", "text": "DISCOUNT10"},
    ], align="center")
    assert '<tg-button-row align="center">' in btn_row
    assert 'type="url"' in btn_row and 'style="primary"' in btn_row
    assert 'type="copy_text"' in btn_row and 'text="DISCOUNT10"' in btn_row

    print("✅ All rich UI builder self-checks passed successfully.")
```

