# Thinking Drafts & Streaming (Telegram Bot API 10.3)

This reference covers the `<tg-thinking>` tag, the `sendRichMessageDraft` method, and the full lifecycle of AI-agent thinking and draft streaming inside Telegram rich messages.

---

## Overview

Modern AI agents (ChatGPT, Claude, Gemini) surface a "thinking" or "reasoning" state before delivering a final answer. Telegram Bot API 10.3 brings this pattern natively into the chat UI through two primitives:

1. **`<tg-thinking>` tag** — a rich HTML element that renders as a frosted/dimmed bubble with an animated shimmer/pulse effect, representing the agent's reasoning state.
2. **`sendRichMessageDraft` method** — a dedicated API method that renders a live, ephemeral draft bubble in the chat without recording it into permanent message history.

Together, they replace the legacy workarounds (`sendChatAction(typing)` and `editMessageText` spam) with a purpose-built, rate-limit-safe, visually polished streaming experience.

### فارسی — مرور کلی
تلگرام در نسخه ۱۰.۳ دو قابلیت جدید برای ربات‌های هوش مصنوعی معرفی کرده:
- تگ `<tg-thinking>` که حالت «در حال فکر کردن» را با حباب مات و انیمیشن لرزشی نمایش می‌دهد.
- متد `sendRichMessageDraft` که یک حباب پیش‌نویس زنده در چت نمایش می‌دهد بدون ثبت در تاریخچه دائمی.

---

## Comparison: Legacy vs `sendRichMessageDraft`

| Approach | Visual UX | Rate Limits | History Impact | Concurrent Chats |
|:---|:---|:---|:---|:---|
| `sendChatAction("typing")` | Small "typing…" indicator in chat header only | Must repeat every 5s; no content preview | None | Safe |
| `editMessageText` (progressive) | Full message replacement each update; causes UI flicker | High risk of `429 Too Many Requests` at >2 req/s | Pollutes message history with intermediate states; notification spam | Risky at scale |
| **`sendRichMessageDraft`** | **Native draft bubble inline in chat; smooth transitions** | **Telegram-managed; no 429 if ≥300ms apart** | **None — draft is ephemeral, never in history** | **Safe** |

### Key Advantages of `sendRichMessageDraft`

- **No message history pollution:** Drafts are ephemeral — they exist only as transient UI state on the client. When the final message arrives, Telegram seamlessly replaces the draft bubble.
- **No 429 rate-limit risk:** Unlike `editMessageText` spam, `sendRichMessageDraft` is designed for streaming updates. Maintaining ≥300ms between calls avoids any throttling.
- **Rich content in drafts:** Drafts accept the full `rich_message` payload — tables, buttons, math, media — not just plain text.
- **Automatic cleanup:** When `sendRichMessage` or `sendMessage` is called for the same chat, Telegram automatically clears the draft bubble. No manual deletion needed.
- **Stop generation UX:** The `can_stop` parameter shows a native stop button, and `keep_on_stop` preserves partial output if the user taps it.

### فارسی — مقایسه روش‌های قدیمی با `sendRichMessageDraft`
- `sendChatAction("typing")` فقط یک نشانگر کوچک «در حال نوشتن» در بالای چت نشان می‌دهد، بدون هیچ محتوایی.
- `editMessageText` باعث لرزش رابط کاربری، ریسک خطای ۴۲۹ و آلودگی تاریخچه می‌شود.
- `sendRichMessageDraft` یک حباب زنده و موقت با محتوای ریچ نمایش می‌دهد، بدون ثبت در تاریخچه و بدون خطای نرخ.

---

## `<tg-thinking>` Tag

### Behavior

The `<tg-thinking>` tag is a **draft-only** rich HTML element. The client renders its content inside a visually distinct bubble:
- **Frosted/dimmed background** with reduced opacity.
- **Animated shimmer/pulse effect** indicating active processing.
- **Supports bidirectional text** via the parent `is_rtl` parameter.
- **Ephemeral by design:** `<tg-thinking>` must only appear inside `sendRichMessageDraft` payloads. It is **not valid** in final messages sent via `sendRichMessage` or `sendMessage`. Including it in a final message will cause it to be stripped or rejected.

### Syntax

```html
<tg-thinking>Analyzing your request and preparing a detailed response…</tg-thinking>
```

Persian / RTL example:

```html
<tg-thinking>در حال تحلیل و ساخت پیام غنی…</tg-thinking>
```

### Combined with Progressive Content

You can include both thinking and partial content in the same draft update to show reasoning alongside accumulated output:

```html
<tg-thinking>Calculating shipping costs for 3 items…</tg-thinking>
<h3>Order Summary</h3>
<p>Processing items: <b>3 of 5</b> complete…</p>
```

As the agent progresses, you update the draft — replacing the thinking text, adding rows to a table, or removing the `<tg-thinking>` block entirely as reasoning completes and only content remains.

### فارسی — تگ `<tg-thinking>`
- این تگ فقط در پیش‌نویس‌ها (`sendRichMessageDraft`) معتبر است و نباید در پیام نهایی استفاده شود.
- کلاینت آن را با حباب مات و انیمیشن لرزشی نمایش می‌دهد.
- برای متن فارسی/عربی، فیلد `is_rtl: true` در `rich_message` تنظیم شود.

---

## `sendRichMessageDraft` Method Specification

### Parameters

| Field | Type | Required | Description |
|:---|:---|:---|:---|
| `chat_id` | `Integer` or `String` | Yes | Target chat ID or `@channelusername`. |
| `draft_id` | `Integer` | Yes | Client-provided unique draft identifier. Used to correlate successive updates to the same draft bubble. |
| `rich_message` | `InputRichMessage` | Yes | Current state of the draft. Accepts `html`, `markdown`, or `blocks` (exactly one). Supports `is_rtl`. |
| `can_stop` | `Boolean` | Optional | When `true`, shows a "Stop generation" button in the client UI. |
| `keep_on_stop` | `Boolean` | Optional | When `true` and user taps stop, the accumulated draft text is preserved as a final message instead of being discarded. |
| `message_thread_id` | `Integer` | Optional | Thread ID for topic/forum chats. |

### Draft ID

The `draft_id` is a client-generated integer that ties together multiple `sendRichMessageDraft` calls into a single evolving draft bubble. Guidelines:

- **Must be unique per active draft session.** Reusing a `draft_id` from a completed (finalized) session starts a new draft.
- **Recommended generation:** Use `message.message_id` from the user's triggering message, a monotonically increasing counter, or `int(time.time() * 1000)` for millisecond-precision uniqueness.
- **Correlation:** The same `draft_id` across multiple calls updates the same bubble in-place rather than creating new bubbles.

### Response

Returns `true` on success. Draft calls do not return a `Message` object (there is no permanent message yet).

### فارسی — مشخصات متد `sendRichMessageDraft`
- فیلد `draft_id` یک عدد صحیح یکتا است که چند فراخوانی متوالی را به یک حباب پیش‌نویس واحد متصل می‌کند.
- فیلد `can_stop` دکمه «توقف تولید» را در کلاینت نمایش می‌دهد.
- فیلد `keep_on_stop` در صورت توقف توسط کاربر، متن تولیدشده تا آن لحظه را حفظ می‌کند.

---

## Execution Lifecycle

### Step-by-Step Flow

```
User sends message/command
        │
        ▼
┌─────────────────────────────────────┐
│ Step 1: Receive update              │
│   Extract chat_id, generate         │
│   draft_id (e.g. message.message_id)│
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│ Step 2: Send thinking draft         │
│   sendRichMessageDraft {            │
│     chat_id, draft_id,              │
│     rich_message: {                 │
│       html: "<tg-thinking>…</…>",   │
│       is_rtl: true/false            │
│     }                               │
│   }                                 │
│   → Client shows frosted bubble     │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│ Step 3: Long-running processing     │
│   (AI inference, DB queries,        │
│    web scraping — 5-20s)            │
│                                     │
│   Optionally: update draft with     │
│   progressive content every 300ms+  │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│ Step 4: Send final message          │
│   sendRichMessage (or sendMessage)  │
│   → Telegram auto-replaces draft    │
│     bubble with final content       │
└─────────────────────────────────────┘
```

### Draft TTL (~30 seconds)

Telegram maintains a draft bubble for approximately **30 seconds** from the last `sendRichMessageDraft` call. If no update or final message arrives within this window, the draft bubble disappears silently from the client UI.

**Implication:** For long-running tasks exceeding 30 seconds, you **must** periodically refresh the draft (e.g., every 15–25 seconds) with updated thinking text to keep the bubble alive:

```python
# Keep-alive pattern for long tasks
while not task_complete:
    await send_thinking_draft(chat_id, draft_id, f"Still processing… ({elapsed}s)")
    await asyncio.sleep(15)
```

### Handling `stopped_message_generation`

When `can_stop: true` is set and the user taps the stop button, Telegram sends an update of type `stopped_message_generation` containing the `chat_id` and `draft_id`. Your bot should:

1. Cancel the background task (LLM inference, etc.).
2. If `keep_on_stop` was `true`, send the partial result as a final `sendRichMessage`.
3. If `keep_on_stop` was `false`, send nothing — Telegram discards the draft automatically.

### فارسی — چرخه اجرا
۱. دریافت پیام کاربر و ساخت `draft_id`.
۲. ارسال پیش‌نویس با `<tg-thinking>` — حباب مات نمایش داده می‌شود.
۳. پردازش طولانی (استنتاج مدل، کوئری دیتابیس). در صورت نیاز، هر ۱۵ ثانیه پیش‌نویس را بازنویسی کنید.
۴. ارسال پیام نهایی — تلگرام حباب پیش‌نویس را به‌صورت خودکار جایگزین می‌کند.

---

## Implementation Recipes

### Python — Raw `httpx` (async)

```python
import httpx
import asyncio
import time

BOT_TOKEN = "YOUR_BOT_TOKEN"
BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

async def thinking_lifecycle(chat_id: int, user_message_id: int):
    draft_id = user_message_id  # or int(time.time() * 1000)

    async with httpx.AsyncClient() as client:
        # Step 1: Send thinking draft
        await client.post(f"{BASE}/sendRichMessageDraft", json={
            "chat_id": chat_id,
            "draft_id": draft_id,
            "rich_message": {
                "html": "<tg-thinking>Analyzing your request…</tg-thinking>",
            },
            "can_stop": True,
            "keep_on_stop": True,
        })

        # Step 2: Simulate long-running AI inference
        await asyncio.sleep(5)

        # Step 3: Optionally update draft with progressive content
        await client.post(f"{BASE}/sendRichMessageDraft", json={
            "chat_id": chat_id,
            "draft_id": draft_id,
            "rich_message": {
                "html": (
                    "<tg-thinking>Formatting results…</tg-thinking>"
                    "<p>Found <b>3 matching records</b>.</p>"
                ),
            },
        })

        await asyncio.sleep(2)

        # Step 4: Send final message — draft auto-clears
        await client.post(f"{BASE}/sendRichMessage", json={
            "chat_id": chat_id,
            "rich_message": {
                "html": (
                    "<h3>Search Results</h3>"
                    "<p>Found <b>3 records</b> matching your query.</p>"
                    "<table bordered compact>"
                    "<tr><th>ID</th><th>Name</th><th>Status</th></tr>"
                    "<tr><td>1</td><td>Alpha</td><td>Active</td></tr>"
                    "<tr><td>2</td><td>Beta</td><td>Pending</td></tr>"
                    "<tr><td>3</td><td>Gamma</td><td>Active</td></tr>"
                    "</table>"
                ),
            },
        })
```

### Python — `requests` (synchronous)

```python
import requests
import time

BOT_TOKEN = "YOUR_BOT_TOKEN"
BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

def thinking_lifecycle_sync(chat_id: int):
    draft_id = int(time.time() * 1000)

    # Step 1: Thinking draft
    requests.post(f"{BASE}/sendRichMessageDraft", json={
        "chat_id": chat_id,
        "draft_id": draft_id,
        "rich_message": {
            "html": "<tg-thinking>Processing your request…</tg-thinking>",
        },
    })

    # Step 2: Simulate work
    time.sleep(5)

    # Step 3: Final message
    requests.post(f"{BASE}/sendRichMessage", json={
        "chat_id": chat_id,
        "rich_message": {
            "html": "<p><b>Done!</b> Your report is ready.</p>",
        },
    })
```

### Python — `urllib.request` (zero dependencies)

```python
import urllib.request
import json
import time

BOT_TOKEN = "YOUR_BOT_TOKEN"
BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

def _post(method: str, payload: dict) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{BASE}/{method}",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def thinking_lifecycle_stdlib(chat_id: int):
    draft_id = int(time.time() * 1000)

    _post("sendRichMessageDraft", {
        "chat_id": chat_id,
        "draft_id": draft_id,
        "rich_message": {
            "html": "<tg-thinking>Thinking…</tg-thinking>",
        },
    })

    time.sleep(5)

    _post("sendRichMessage", {
        "chat_id": chat_id,
        "rich_message": {
            "html": "<p><b>Complete.</b></p>",
        },
    })
```

### Python — aiogram 3.x (Custom `TelegramMethod`)

```python
from typing import Any, Optional
from aiogram import Bot, Router, F
from aiogram.methods.base import TelegramMethod
from aiogram.filters import Command
from aiogram.types import Message
import asyncio

class SendRichMessageDraft(TelegramMethod[bool]):
    __returning__ = bool
    __api_method__ = "sendRichMessageDraft"

    chat_id: int | str
    draft_id: int
    rich_message: dict[str, Any]
    can_stop: Optional[bool] = None
    keep_on_stop: Optional[bool] = None
    message_thread_id: Optional[int] = None

class SendRichMessage(TelegramMethod[Message]):
    __returning__ = Message
    __api_method__ = "sendRichMessage"

    chat_id: int | str
    rich_message: dict[str, Any]
    message_thread_id: Optional[int] = None
    disable_notification: Optional[bool] = None
    protect_content: Optional[bool] = None
    reply_markup: Optional[Any] = None

router = Router(name="thinking_router")

@router.message(Command("think"))
async def cmd_think(message: Message, bot: Bot):
    chat_id = message.chat.id
    draft_id = message.message_id

    # Send thinking draft
    await bot(SendRichMessageDraft(
        chat_id=chat_id,
        draft_id=draft_id,
        rich_message={
            "html": "<tg-thinking>در حال تحلیل درخواست شما…</tg-thinking>",
            "is_rtl": True,
        },
        can_stop=True,
        keep_on_stop=True,
    ))

    # Simulate AI inference
    await asyncio.sleep(5)

    # Send final response — draft auto-clears
    await bot(SendRichMessage(
        chat_id=chat_id,
        rich_message={
            "html": "<h3>نتیجه تحلیل</h3><p>پردازش با موفقیت انجام شد.</p>",
            "is_rtl": True,
        },
    ))
```

### TypeScript — grammY

```typescript
import { Bot, Api } from "grammy";

const bot = new Bot("YOUR_BOT_TOKEN");

bot.command("think", async (ctx) => {
  const chatId = ctx.chat.id;
  const draftId = ctx.message?.message_id ?? Date.now();

  // Step 1: Send thinking draft
  await ctx.api.raw.sendRichMessageDraft({
    chat_id: chatId,
    draft_id: draftId,
    rich_message: {
      html: "<tg-thinking>Analyzing your request…</tg-thinking>",
    },
    can_stop: true,
    keep_on_stop: true,
  });

  // Step 2: Simulate AI processing
  await new Promise((r) => setTimeout(r, 5000));

  // Step 3: Send final message — draft auto-clears
  await ctx.api.raw.sendRichMessage({
    chat_id: chatId,
    rich_message: {
      html: "<h3>Analysis Complete</h3><p>Found <b>3 results</b>.</p>",
    },
  });
});

bot.start();
```

### TypeScript — Cloudflare Workers (fetch-based)

```typescript
interface Env {
  BOT_TOKEN: string;
}

async function callTelegram(
  token: string,
  method: string,
  payload: Record<string, unknown>,
): Promise<unknown> {
  const resp = await fetch(
    `https://api.telegram.org/bot${token}/${method}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
  );
  return resp.json();
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const update = await request.json() as any;
    const message = update?.message;
    if (!message?.text?.startsWith("/think")) {
      return new Response("ok");
    }

    const chatId = message.chat.id;
    const draftId = message.message_id;

    // Send thinking draft (non-blocking from client perspective)
    await callTelegram(env.BOT_TOKEN, "sendRichMessageDraft", {
      chat_id: chatId,
      draft_id: draftId,
      rich_message: {
        html: "<tg-thinking>Processing your request…</tg-thinking>",
      },
      can_stop: true,
    });

    // Simulate work (note: Workers have a 30s CPU limit on paid plan)
    await new Promise((r) => setTimeout(r, 3000));

    // Final response
    await callTelegram(env.BOT_TOKEN, "sendRichMessage", {
      chat_id: chatId,
      rich_message: {
        html: "<p><b>Done!</b> Your analysis is ready.</p>",
      },
    });

    return new Response("ok");
  },
};
```

---

## Error Handling & Edge Cases

### Rate Limiting

- **Minimum interval:** Keep at least **300ms** between consecutive `sendRichMessageDraft` calls to the same `chat_id`. Faster calls risk `429 Too Many Requests`.
- **Recommended interval:** 300ms–500ms for token streaming; 1–5 seconds for phase-based thinking updates.
- **Per-chat, not global:** Rate limits on drafts are per-chat. Concurrent draft sessions across different chats are independent.

### Draft TTL Expiry

- The draft bubble disappears after **~30 seconds** of silence (no `sendRichMessageDraft` update and no final message).
- For tasks longer than 25 seconds, implement a **keep-alive loop** that re-sends the thinking draft every 15–20 seconds.
- If the draft expires before the final message, the user sees a gap — no thinking bubble, then a final message appearing from nowhere. Always finalize before TTL or keep the draft alive.

### `stopped_message_generation` Update

When `can_stop: true` is set and the user taps stop:

```json
{
  "update_id": 123456789,
  "stopped_message_generation": {
    "chat": { "id": 123456789, "type": "private" },
    "draft_id": 987654321,
    "date": 1773660000
  }
}
```

Handle this by:
1. Canceling the running task / LLM stream.
2. If `keep_on_stop` was `true`, send accumulated partial output as a final `sendRichMessage`.
3. If `keep_on_stop` was `false` or not set, do nothing — the draft is discarded.

### Common Errors

| Error | Cause | Fix |
|:---|:---|:---|
| `400 Bad Request: draft_id is required` | Missing `draft_id` in payload. | Always include a non-zero integer `draft_id`. |
| `400 Bad Request: exactly one of html, markdown, or blocks must be specified` | Multiple content keys in `rich_message`. | Pass exactly one of `html`, `markdown`, or `blocks`. |
| `429 Too Many Requests` | Sending drafts faster than 300ms interval. | Throttle to ≥300ms between calls. Implement exponential backoff. |
| `400 Bad Request: CHAT_NOT_FOUND` | Invalid `chat_id` or bot not in chat. | Verify chat exists and bot is a member. |

### فارسی — مدیریت خطا
- فاصله حداقل ۳۰۰ میلی‌ثانیه بین فراخوانی‌های `sendRichMessageDraft` رعایت شود.
- پیش‌نویس بعد از حدود ۳۰ ثانیه بدون بروزرسانی منقضی می‌شود؛ برای پردازش‌های طولانی، هر ۱۵-۲۰ ثانیه پیش‌نویس را تازه‌سازی کنید.
- در صورت توقف توسط کاربر، آپدیت `stopped_message_generation` دریافت می‌شود.

---

## Patterns & Best Practices

### 1. Phase-Based Thinking Updates

Update the thinking text to reflect the current processing phase:

```python
phases = [
    "Reading your message…",
    "Querying the knowledge base…",
    "Generating response…",
    "Formatting output…",
]
for phase in phases:
    await bot(SendRichMessageDraft(
        chat_id=chat_id,
        draft_id=draft_id,
        rich_message={"html": f"<tg-thinking>{html.escape(phase)}</tg-thinking>"},
    ))
    await asyncio.sleep(3)  # Actual work per phase
```

### 2. Progressive Content Accumulation

Stream partial results alongside thinking:

```python
accumulated = ""
async for chunk in llm_stream():
    accumulated += chunk
    await bot(SendRichMessageDraft(
        chat_id=chat_id,
        draft_id=draft_id,
        rich_message={
            "html": f"<tg-thinking>Generating…</tg-thinking><p>{html.escape(accumulated)}</p>",
        },
    ))
    await asyncio.sleep(0.3)  # Respect 300ms minimum
```

### 3. RTL / Bilingual Thinking

For bots serving Persian, Arabic, or Hebrew users:

```python
await bot(SendRichMessageDraft(
    chat_id=chat_id,
    draft_id=draft_id,
    rich_message={
        "html": "<tg-thinking>در حال تحلیل و ساخت پیام غنی…</tg-thinking>",
        "is_rtl": True,
    },
))
```

For bilingual bots that may serve both LTR and RTL users, detect direction from the user's message language or locale setting:

```python
def detect_rtl(text: str) -> bool:
    """Check if the first strong character is RTL (Arabic, Hebrew, Persian)."""
    for ch in text:
        if "֐" <= ch <= "ࣿ" or "ﭐ" <= ch <= "﷿" or "ﹰ" <= ch <= "﻿":
            return True
        if ch.isalpha():
            return False
    return False
```

### 4. Graceful Degradation

If `sendRichMessageDraft` is unavailable (e.g., bot API server not yet upgraded), fall back to `sendChatAction`:

```python
async def send_thinking_or_fallback(bot: Bot, chat_id: int, draft_id: int, text: str):
    try:
        await bot(SendRichMessageDraft(
            chat_id=chat_id,
            draft_id=draft_id,
            rich_message={"html": f"<tg-thinking>{html.escape(text)}</tg-thinking>"},
        ))
    except Exception:
        await bot.send_chat_action(chat_id=chat_id, action="typing")
```

---

## Anti-Patterns

1. **Using `<tg-thinking>` in final messages.** The tag is draft-only. Including it in `sendRichMessage` causes it to be stripped or rejected. Always remove `<tg-thinking>` before sending the final output.

2. **Reusing `draft_id` across unrelated requests.** Each user request should get its own `draft_id`. Reusing one from a previous, completed interaction can cause confusing UI state.

3. **Sending drafts faster than 300ms.** This triggers `429` errors and degrades the experience. Implement a minimum delay between calls.

4. **Forgetting draft TTL on long tasks.** A draft that isn't refreshed within ~30 seconds silently disappears. Users see no indication of ongoing work. Always implement keep-alive for tasks exceeding 25 seconds.

5. **Not handling `stopped_message_generation`.** Ignoring the stop signal wastes compute and confuses users who expect the bot to stop generating.

6. **Mixing `editMessageText` with drafts.** Don't send a real message via `sendMessage` and then try to edit it while also having an active draft. Use drafts for the entire streaming phase, then finalize with a single `sendRichMessage`.
