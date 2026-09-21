# Rich formatting overview

## Table of contents

- [Source of truth](#source-of-truth)
- [Core methods](#core-methods)
- [InputRichMessage](#inputrichmessage)
- [Limits](#limits)
- [Rich HTML](#rich-html)
- [Rich Markdown](#rich-markdown)
- [JSON blocks](#json-blocks)
- [Editing](#editing)
- [RTL and entity detection](#rtl-and-entity-detection)
- [Date and time](#date-and-time)
- [Safety rules](#safety-rules)
- [Decision guide](#decision-guide)

## Source of truth

This reference describes the Telegram Bot API 10.3 contract verified on 2026-09-21. If Telegram's live documentation changes, update this file and `SOURCES.md` before relying on old examples.

## Core methods

### `sendRichMessage`

Use `sendRichMessage` to persist a rich message. Important parameters include:

- `chat_id`
- `rich_message`
- `business_connection_id`
- `message_thread_id`
- `direct_messages_topic_id`
- `ephemeral_message_parameters`
- `disable_notification`
- `protect_content`
- `allow_paid_broadcast`
- `message_effect_id`
- `suggested_post_parameters`
- `reply_parameters`
- `reply_markup`

If the rich message contains media, the bot must have permission to send that media type in the target chat.

### `sendRichMessageDraft`

Use this only for temporary rich draft streaming in a private chat. It returns `True`, not a persistent `Message`. See `thinking-drafts-and-streaming.md`.

### `sendMessageDraft`

Use this for temporary plain-text draft streaming. An empty text value displays Telegram's native "Thinking..." placeholder. Finalize with a persistent message when needed.

### `editMessageText`

Telegram does **not** define an `editRichMessageText` method. To replace an existing text/rich message with rich content, use `editMessageText` with its `rich_message` parameter according to the current Bot API method signature.

## InputRichMessage

`InputRichMessage` accepts exactly one content source:

- `html`
- `markdown`
- `blocks`

Optional companion fields:

- `media`: media objects referenced by rich HTML/Markdown through Telegram media identifiers.
- `is_rtl`: force right-to-left layout.
- `skip_entity_detection`: disable automatic detection of URLs, email addresses, username mentions, hashtags, cashtags, bot commands, and phone numbers.

Invalid pattern:

```json
{
  "html": "<p>Hello</p>",
  "blocks": [{"type": "paragraph"}]
}
```

Valid pattern:

```json
{
  "html": "<p>Hello</p>",
  "is_rtl": false
}
```

## Limits

Telegram documents these rich-message limits:

| Limit | Maximum |
| --- | ---: |
| UTF-8 characters | 32,768 |
| blocks, including nested/list/table-row/quotation/detail blocks | 500 |
| nesting levels | 16 |
| media attachments | 50 |
| table columns | 20 |

Treat them as preflight constraints. Keep headroom for dynamically generated content.

## Rich HTML

Rich HTML is the default choice in this repository for UI-like bot messages.

Telegram's documented rich HTML includes conventional inline formatting plus structural/custom tags such as:

- headings `h1` through `h6`
- paragraphs and lists
- `blockquote`, including `expandable`
- `aside`/pull quotation
- `details` and `summary`
- `table`, `tr`, `th`, `td`, `caption`
- `tg-collage`
- `tg-slideshow`
- `tg-map`
- `tg-document`
- `tg-button` and `tg-button-row`
- `tg-time`
- `tg-math` and `tg-math-block`
- `tg-emoji`
- `tg-reference`
- draft-only `tg-thinking`

Only documented tags are supported. Table cells accept inline formatting only.

Example:

```html
<h3>Order status</h3>
<p>Your order is ready.</p>
<table bordered striped compact>
  <tr><th>Item</th><th align="right">Qty</th></tr>
  <tr><td>Keyboard</td><td align="right">1</td></tr>
</table>
<tg-button-row align="center">
  <tg-button type="callback_data" style="primary" data="order:details">Details</tg-button>
</tg-button-row>
```

### Named entities

Do not assume every HTML named entity is accepted. Telegram documents a limited set of named entities for rich HTML. Escaping `&`, `<`, `>`, quotes, and apostrophes is sufficient for most dynamic values; prefer numeric entities for unusual characters if encoding is required.

## Rich Markdown

Telegram's Rich Markdown is compatible with GitHub-Flavored Markdown where possible and can include supported rich HTML.

Use Markdown when content is primarily authored text. Use HTML when you need predictable structural UI.

Important rules:

- Media appears as separate media blocks.
- Table cells contain only inline formatting.
- Formula source is raw LaTeX.
- Markdown is not parsed inside most block HTML tags; documented exceptions include `details`, `tg-collage`, and `tg-slideshow`.

## JSON blocks

Use JSON blocks when application code already models UI structurally or when schema validation is preferable to markup parsing.

Every block has a documented `type`. Do not invent wrapper fields from DOM terminology.

Example table:

```json
{
  "blocks": [
    {
      "type": "table",
      "cells": [
        [
          {"text": "Item", "is_header": true},
          {"text": "Qty", "is_header": true, "align": "right"}
        ],
        [
          {"text": "Keyboard"},
          {"text": "1", "align": "right"}
        ]
      ],
      "is_bordered": true,
      "is_compact": true
    }
  ]
}
```

The exact `RichText` JSON representation may be richer than a plain string in generated framework types. Prefer framework-native model classes when producing typed block trees.

## Editing

When editing an existing message:

1. Use the documented `editMessageText` method.
2. Supply `rich_message` when replacing content with a rich message.
3. Preserve or update `reply_markup` intentionally.
4. Do not create a local helper name that looks like an official Telegram method unless it is clearly marked as an application helper.

For ephemeral messages, use the dedicated ephemeral edit methods and see `ephemeral-messages.md`.

## RTL and entity detection

Set `is_rtl: true` for a message that must be rendered right-to-left. Do not depend on heuristics when layout direction is a product requirement.

Use `skip_entity_detection: true` when automatic link/mention/phone/etc. recognition would harm the intended UI. This is independent of explicit rich entities you define.

For mixed Persian/Arabic and Latin identifiers, prefer structural separation or inline code where it improves readability. Treat detailed visual BiDi behavior as client behavior, not as a Bot API guarantee.

## Date and time

Rich messages can use `tg-time` with Unix seconds. Telegram documents the format grammar:

```text
r|w?[dD]?[tT]?
```

Examples:

```html
<tg-time unix="1647531900" format="wDT">scheduled time</tg-time>
<tg-time unix="1647531900" format="r">relative time</tg-time>
```

`r` is the relative-time form. Follow the documented grammar rather than generating arbitrary flag order.

## Safety rules

- Escape untrusted text before interpolation into HTML.
- Escape attribute values separately and validate URL schemes.
- Prefer framework-native structured objects when user input controls complex block content.
- Do not trust a successful parser result to mean a URL is safe for your application.
- Keep secrets out of rich content and callbacks.
- Do not branch on exact human-readable Bot API error descriptions.

## Decision guide

Choose:

- HTML for polished, hand-composed bot UI.
- Markdown for document-like generated content.
- JSON blocks for typed component systems.
- legacy text for simple messages and explicit compatibility fallback.

Then read the feature-specific reference before implementation.
