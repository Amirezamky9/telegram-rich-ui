---
name: telegram-rich-ui
description: "Telegram Bot API 10.3 Rich Message UI: tables, slideshows, inline buttons, custom emojis, ephemeral messages, AI thinking drafts, and streaming."
version: 1.1.0
author: Coding Supervisor
license: MIT
platforms: [linux, macos, windows]
tags: [telegram, bot-api-10-3, rich-messages, ui, tables, slideshow, custom-emoji, aiogram, grammy, thinking, drafts, streaming]
metadata:
  hermes:
    tags: [telegram, bot-api-10-3, rich-messages, ui, tables, slideshow, custom-emoji, aiogram, grammy, thinking, drafts, streaming]
    related_skills: []
---

# Telegram Rich UI (Bot API 10.3)

Telegram Bot API 10.3 introduces a structured Rich Message presentation layer that moves beyond legacy monospace ASCII tables and unstyled text. Bots can now render rich document structures including compact responsive tables, interactive multi-media slideshows, styled inline buttons embedded directly inside text paragraphs, custom emoji icons, LaTeX mathematics, user-private ephemeral group messages, and AI-agent thinking/reasoning states with live draft streaming via `<tg-thinking>` and `sendRichMessageDraft`.

## When to Use

- **Triggers:**
  - Styling modern Telegram bot messages with native UI elements instead of ASCII art tables or monospace formatting.
  - Building rich e-commerce product catalogs, comparison sheets, financial invoices, or order summaries with `<table bordered striped compact>`.
  - Rendering multi-item carousels or image galleries using `<tg-slideshow>` or grouped image grids with `<tg-collage>`.
  - Adding in-text buttons (`<tg-button>`, `<tg-button-row>`) with semantic color styles (`primary`, `success`, `danger`), clipboard copy (`copy_text`), or disabled states (`disabled`).
  - Rendering custom emoji icons (`<tg-emoji>`) with unicode fallbacks or attaching custom emoji icons to keyboard buttons (`icon_custom_emoji_id`).
  - Formatting dates with automatic client localization (`<tg-time>`) or LaTeX math formulas (`<tg-math>`, `<tg-math-block>`).
  - Sending private-to-user ephemeral responses inside high-volume groups via `ephemeral_message_parameters`.
  - Showing AI reasoning/thinking state with `<tg-thinking>` inside `sendRichMessageDraft` — renders a frosted, shimmer-animated bubble representing agent cognition.
  - Streaming progressive AI generation updates using `sendRichMessageDraft` with `can_stop` and `keep_on_stop`.
  - Building AI agents that display phase-based thinking (e.g. "Analyzing…", "Querying knowledge base…", "Formatting results…") before delivering a final rich response.
  - Replacing legacy `sendChatAction(typing)` or `editMessageText` polling with native ephemeral draft bubbles that auto-clear on finalization.
  - Porting legacy HTML/Markdown `sendMessage` bots to Bot API 10.3 `sendRichMessage` without breaking legacy clients.

- **Don't use for:**
  - Simple plain text messages without rich elements (standard `sendMessage` with no parse mode is faster, cheaper, and lighter).
  - Legacy Bot API server environments (versions prior to Bot API 10.1 cannot interpret `rich_message` payloads).
  - High-throughput broadcast alerts where client-side rendering latency must be strictly minimized.
  - Heavy multi-page documents that exceed 32,768 characters (deliver as external PDF/web pages or split across messages).
  - Sending ephemeral messages inside broadcast channels (ephemeral delivery is strictly supported in private chats and groups).

### Capability Comparison: Legacy vs Bot API 10.3

| Feature | Legacy `sendMessage` (parse_mode) | Bot API 10.3 `sendRichMessage` |
|:---|:---|:---|
| Document Structure | Flat string with character spans | Hierarchical block tree (`h1`–`h6`, `p`, lists) |
| Tables | Unaligned monospace `<pre>` | Native responsive `<table bordered striped compact>` |
| Media Groups | Separate `sendMediaGroup` (no text flow) | Embedded `<tg-slideshow>` and `<tg-collage>` in message |
| In-text Buttons | None (keyboards only below bubble) | Native `<tg-button>` flowing inside paragraphs |
| Ephemeral Messages | Not supported | User-private responses via `EphemeralMessageParameters` |
| Token Streaming | Full message replacement via `editMessageText` | Progressive drafts via `sendRichMessageDraft` |
| AI Thinking State | Not supported (only `sendChatAction("typing")` header indicator) | Native `<tg-thinking>` frosted bubble with shimmer animation via `sendRichMessageDraft` |

## Architecture Overview

### Rich Messages vs Legacy `sendMessage` + `parse_mode`

In Bot API 1.0–10.0, formatting was restricted to flat character ranges inside `text` with `parse_mode: 'HTML'` or `'MarkdownV2'`. The message body was strictly a single flat string, and keyboards could only be attached externally below the message bubble as `reply_markup`. Complex structures like tables had to be faked using monospace code blocks (`<pre>`), which distorted on mobile screens and lacked cell alignment.

Bot API 10.1+ (expanded in 10.2 and 10.3) introduces the dedicated `sendRichMessage` endpoint and `rich_message` payload object:
1. **Source Formats:** You supply either `html` (Rich HTML string), `markdown` (Rich Markdown string), or `blocks` (structured JSON array of `InputRichBlock` objects). Exactly one source format is permitted per request.
2. **Block Tree Model:** The parser compiles the source into top-level container blocks: Headings (`h1`–`h6`), Paragraphs (`p`), Tables (`table`), Media containers (`tg-slideshow`, `tg-collage`), Lists (`ul`, `ol`), Blockquotes (`blockquote`), and Button rows (`tg-button-row`).
3. **Inline Flow & Entities:** Within blocks, text flows inline alongside rich entities: formatting (`<b>`, `<i>`, `<u>`, `<s>`), disclosures (`<tg-spoiler>`, `<details>`), inline buttons (`<tg-button>`), custom emojis (`<tg-emoji>`), math (`<tg-math>`), and localized time (`<tg-time>`).
4. **Bidirectional Layout (RTL/LTR):** Rich messages support the `is_rtl` parameter. Modern clients perform "first strong character" heuristic detection to align paragraphs to the right for Persian, Arabic, or Hebrew content.

### Payload Schema and Block Compilation

The payload passed to `sendRichMessage` wraps content inside the `rich_message` container:

```json
{
  "chat_id": 123456789,
  "rich_message": {
    "html": "<p>Invoice summary</p><table bordered compact>...</table>",
    "is_rtl": false
  },
  "reply_markup": { ... }
}
```

Telegram's parsing engine converts this string into an Abstract Syntax Tree (AST) of structured blocks. When `blocks` JSON is passed directly, developers gain granular control over block identifiers and media mapping without running a string parser.

### Client Fallback Behavior

When a Bot API 10.3 rich message is delivered to an outdated Telegram client:
- **Block Fallback:** Tables and blocks degrade into structured text paragraphs separated by line breaks; tabular column alignment degrades gracefully rather than disappearing.
- **Custom Emoji Fallback:** The inner text inside `<tg-emoji emoji-id="...">FALLBACK</tg-emoji>` is rendered as plain unicode text.
- **Inline Buttons:** Client versions lacking inline flow support display rich buttons as attached keyboard rows below the text bubble.
- **Media Fallback:** Slideshows degrade to standard album views or the first slide media item with caption.

### AI Thinking & Draft Streaming

Bot API 10.3 introduces a purpose-built lifecycle for AI-agent thinking states, replacing legacy workarounds:

1. **`<tg-thinking>` Tag:** A draft-only rich HTML element that the client renders as a frosted/dimmed bubble with an animated shimmer/pulse effect. Represents the agent's reasoning state (e.g., `<tg-thinking>در حال تحلیل و ساخت پیام غنی…</tg-thinking>`). It is **ephemeral/draft-only** — it must not appear in final messages sent via `sendRichMessage`.
2. **`sendRichMessageDraft` Method:** Renders a live draft bubble directly in the chat without recording it into permanent message history. Accepts the full `rich_message` payload (including `is_rtl` for Persian/Arabic). Telegram holds and updates this draft bubble automatically.
3. **Automatic Transition:** When the bot sends the final message via `sendRichMessage` (or `sendMessage`), Telegram seamlessly replaces and clears the draft bubble — no extra API calls needed.
4. **Draft TTL (~30s):** Drafts expire after approximately 30 seconds of silence. For long-running tasks, refresh the draft every 15–20 seconds.
5. **Stop Generation:** Setting `can_stop: true` shows a native stop button; `keep_on_stop: true` preserves accumulated content if the user taps stop. Telegram delivers a `stopped_message_generation` update for cancellation handling.
6. **RTL Support:** Pass `is_rtl: true` in the `rich_message` object for Persian, Arabic, or Hebrew thinking text to ensure correct bidirectional rendering.

#### Payload Example

```json
{
  "chat_id": 123456789,
  "draft_id": 987654321,
  "rich_message": {
    "html": "<tg-thinking>در حال پردازش…</tg-thinking>",
    "is_rtl": true
  },
  "can_stop": true,
  "keep_on_stop": true
}
```

## Reference Routing

| Resource | Scope / When to Read |
|:---|:---|
| `references/rich-formatting-overview.md` | Core Bot API 10.3 methods (`sendRichMessage`, `editRichMessageText`), root `rich_message` payload shapes, full inline-entity coverage, math formulas, timestamps, and entity auto-detection. |
| `references/tables-and-grids.md` | Tabular syntax (`<table bordered striped compact>`), `<caption>`, cell alignment (`align`, `valign`), spanning (`colspan`, `rowspan`), grid invariants, and worked invoice/cart examples. |
| `references/slideshow-and-media.md` | Media carousels (`<tg-slideshow>`), collages (`<tg-collage>`), `file_id` vs HTTPS URLs, audio/video embeds, geolocations (`<tg-map>`), and progressive caching. |
| `references/custom-emojis-and-stickers.md` | Custom emojis (`<tg-emoji>`), Telegram Premium owner prerequisites, querying IDs via `getCustomEmojiStickers`, button icon IDs, and fallback handling. |
| `references/rich-buttons-and-colors.md` | In-text rich buttons (`<tg-button>`), row alignment (`<tg-button-row>`), semantic color styles (`primary`, `success`, `danger`), clipboard copy actions, disabled states, and block JSON. |
| `references/aiogram-python-recipes.md` | Python aiogram 3.30+ production recipes: native methods, custom `TelegramMethod` RPC fallback, HTML builders, escaping, callback handlers, and graceful degradation. |
| `references/grammy-cloudflare-recipes.md` | TypeScript grammY on Cloudflare Workers: timing-safe secret verification, typed raw client, HTML builders, callback handlers, and channel administrative pre-checks. |
| `references/thinking-drafts-and-streaming.md` | AI thinking state (`<tg-thinking>`), `sendRichMessageDraft` specification, draft TTL, `stopped_message_generation` handling, comparison with legacy approaches, implementation recipes (Python/TypeScript), and streaming best practices. |
| `scripts/thinking_draft_demo.py` | Runnable zero-dependency Python demo: full `sendRichMessageDraft` → `sendRichMessage` lifecycle with CLI arguments (`--token`, `--chat-id`, `--thinking-text`, `--rtl`). |
| `templates/product-catalog-card.html` | Production product card template: photo slideshow carousel, specifications/pricing table, custom emoji accents, and action button rows. |
| `templates/invoice-receipt.html` | Production invoice receipt template: compact striped table, colspan totals, localized `<tg-time>`, tracking code copy button, and Persian RTL variant. |
| `templates/persistent-menu-rich.html` | Production bilingual welcome/navigation portal template: expandable guide, feature status table, and multi-action button rows. |

### Operational Workflow (Using References Together)

1. **Architecture & Format Selection:** Review `references/rich-formatting-overview.md` to choose between HTML, Markdown, or JSON blocks.
2. **Data Presentation:** Use `references/tables-and-grids.md` to format tabular reports, adhering strictly to rectangular grid consistency rules.
3. **Media & Assets:** Use `references/slideshow-and-media.md` and `references/custom-emojis-and-stickers.md` to populate galleries and custom emoji icons.
4. **Interactivity & Ephemeral Routing:** Implement buttons with `references/rich-buttons-and-keyboards.md` and private responses via `references/ephemeral-messages-and-drafts.md`.
5. **AI Thinking & Streaming:** Use `references/thinking-drafts-and-streaming.md` to implement thinking states, draft streaming, and progressive generation with `<tg-thinking>` and `sendRichMessageDraft`. Run `scripts/thinking_draft_demo.py` as a quick verification.
6. **Runtime Integration:** Wire handlers using `references/framework-adapters-and-runtimes.md` and the appropriate template.

## Pitfalls

1. **Mutually Exclusive Payload Keys:** A `rich_message` payload must contain exactly one of `html`, `markdown`, or `blocks`. Passing more than one key causes Telegram API error `400 Bad Request: exactly one of html, markdown, or blocks must be specified`.
2. **Payload Character Limit:** The text representation in `html` or `markdown` must not exceed 32,768 characters. Exceeding this boundary fails with `MESSAGE_TOO_LONG`.
3. **Table Grid Dimensional Inconsistency:** If the sum of `colspan` across columns does not equal the grid column count, or if `rowspan` overlaps an existing cell, mobile clients glitch or drop the table block into an unstyled dump. Always ensure row grid completeness.
4. **Custom Emoji Premium Prerequisite:** Bots cannot send custom emojis to non-Premium users unless the bot owner's Telegram account has an active Telegram Premium subscription. Unsubscribed bots produce plain unicode fallbacks.
5. **Ephemeral Messages in Channels:** Ephemeral messages (`ephemeral_message_parameters`) are strictly supported in groups and supergroups. Invoking them in a broadcast channel returns a `400 Bad Request: ephemeral messages are not supported in channels` error.
6. **Button Style Constraints:** The `style` attribute on buttons only accepts `primary`, `success`, and `danger` (`link` is permitted only on `callback_data` buttons). Arbitrary hex colors are rejected.
7. **Callback Data Size Limit:** Callback data on rich buttons or inline keyboards must not exceed 64 UTF-8 bytes. Larger payloads must be stored in server-side session stores or caches.
8. **Self-Closing XML Tags in HTML:** HTML parsers require standard open/close pairs for custom tags (e.g. `<tg-emoji emoji-id="...">👍</tg-emoji>`). Using self-closing syntax like `<tg-emoji .../>` can cause subsequent sibling nodes to nest incorrectly.
9. **Entity Nesting Invariants:** While bold, italic, and underline can freely nest, interactive entities (e.g. links inside buttons, or buttons inside links) are prohibited and will fail server-side validation.
10. **Draft Expiry and Streaming Discipline:** When streaming tokens via `sendRichMessageDraft`, keep update frequency between 300ms–500ms to avoid hitting rate limits (`429 Too Many Requests`). Always handle `stopped_message_generation` updates.
11. **`<tg-thinking>` in Final Messages:** The `<tg-thinking>` tag is strictly draft-only. Including it in a `sendRichMessage` call causes it to be stripped or rejected. Always remove `<tg-thinking>` from the HTML before sending the final output.
12. **Draft TTL Neglect:** `sendRichMessageDraft` bubbles expire after ~30 seconds of silence. For long-running tasks (AI inference, web scraping), implement a keep-alive loop that refreshes the draft every 15–20 seconds. Failure to refresh causes the bubble to disappear silently, leaving the user with no indication of ongoing work.
13. **Reusing `draft_id` Across Unrelated Requests:** Each user interaction should generate a fresh `draft_id`. Reusing a `draft_id` from a previous completed session can produce confusing UI state where the new draft overwrites or conflicts with stale state.
14. **Mixing `editMessageText` with Draft Streaming:** Do not send a permanent message and edit it while also maintaining an active `sendRichMessageDraft` session. Use drafts exclusively for the streaming phase, then finalize with a single `sendRichMessage`.

## Verification

To confirm a rich message rendered successfully in Telegram:

1. **API Response Check:** Verify the HTTP response status is `200 OK` and the returned JSON contains `{"ok": true, "result": {"message_id": ..., "chat": ...}}`. Confirm that the returned `Message` object includes the expected message structure.
2. **Premium Verification:** Call `getMe` to verify bot credentials. Verify owner Premium status before relying on custom emojis for general public audiences.
3. **Automated Curl Verification:** Test payload syntax directly via curl:
   ```bash
   curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendRichMessage" \
     -H "Content-Type: application/json" \
     -d '{
       "chat_id": "'"$TEST_CHAT_ID"'",
       "rich_message": {
         "html": "<h3>Verification Test</h3><p>Status: <tg-button type=\"copy_text\" text=\"OK\">Active</tg-button></p>"
       }
     }' | jq .
   ```
4. **Python Smoke Test:**
   ```python
   import urllib.request, json, os
   token = os.environ["BOT_TOKEN"]
   payload = json.dumps({
       "chat_id": int(os.environ["TEST_CHAT_ID"]),
       "rich_message": {"html": "<p><b>TeleRich</b> verified.</p>"}
   }).encode()
   req = urllib.request.Request(
       f"https://api.telegram.org/bot{token}/sendRichMessage",
       data=payload, headers={"Content-Type": "application/json"}
   )
   with urllib.request.urlopen(req) as resp:
       assert json.loads(resp.read()).get("ok") is True
   ```
5. **Visual Inspection in Test Chat:** Test the output on both Telegram Desktop and Telegram Mobile (iOS / Android). Confirm:
   - Tables show crisp borders and compact padding without horizontal overflow wrapping.
   - Slideshows allow tapping left/right arrows or swiping between slides.
   - In-text rich buttons trigger expected callbacks or open Mini Apps without disrupting text flow.
   - Text direction (`dir="rtl"` / `dir="ltr"`) renders properly when mixing RTL languages (Persian/Arabic) with English code or links.
6. **Fallback Verification:** Open the sent message in an older Telegram client build or web client to ensure graceful degradation into clean paragraphs.
7. **Thinking Draft Lifecycle Test:** Run the self-contained demo script to verify the full thinking → processing → final message lifecycle:
   ```bash
   python3 scripts/thinking_draft_demo.py --token "$BOT_TOKEN" --chat-id "$TEST_CHAT_ID"
   # RTL variant:
   python3 scripts/thinking_draft_demo.py --token "$BOT_TOKEN" --chat-id "$TEST_CHAT_ID" --rtl
   ```
   Confirm: (a) frosted thinking bubble appears immediately, (b) thinking text updates with progress, (c) final rich message replaces draft seamlessly, (d) no draft artifacts remain in chat history.
