# UI design patterns for Telegram rich messages

## Table of contents

- [Goal](#goal)
- [Choose a surface](#choose-a-surface)
- [Visual hierarchy](#visual-hierarchy)
- [Buttons and actions](#buttons-and-actions)
- [Tables and dense data](#tables-and-dense-data)
- [Media-first cards](#media-first-cards)
- [Edit in place](#edit-in-place)
- [Details and progressive disclosure](#details-and-progressive-disclosure)
- [Persian and RTL](#persian-and-rtl)
- [Loading and AI generation](#loading-and-ai-generation)
- [Mini App handoff](#mini-app-handoff)
- [Accessibility and fallback](#accessibility-and-fallback)
- [Reusable component model](#reusable-component-model)
- [Preflight checklist](#preflight-checklist)

## Goal

A polished Telegram bot UI should feel native to Telegram rather than like a web page squeezed into a chat bubble. Use rich messages to improve hierarchy, scanning, and interaction while keeping the number of simultaneous choices small.

Everything in this file is **project design guidance** unless a Telegram API restriction is explicitly named. Rendering details remain client-owned.

## Choose a surface

Use the smallest surface that fits the task:

- plain `sendMessage` for short conversational responses;
- rich message for structured content, native tables, embedded rich buttons, media layouts, localized time, or RTL control;
- ordinary inline keyboard when controls should sit separately under otherwise ordinary text;
- Mini App when the task becomes form-heavy, stateful, visual, or needs many interactive controls.

Do not move a two-button confirmation flow into a Mini App merely because a Mini App exists.

## Visual hierarchy

Recommended composition:

1. one concise heading;
2. one short status/summary paragraph;
3. one primary structured block (table, media, details, or list);
4. one primary action row;
5. optional secondary action row.

Avoid stacking several headings, multiple wide tables, and several button rows in the same bubble.

Prefer semantic formatting:

- bold for current state or totals;
- code for opaque identifiers/SKUs/tracking codes;
- `tg-time` for dates users should see in local time;
- `details` for secondary explanations;
- `blockquote`/`aside` for quoted material, not generic decoration.

## Buttons and actions

Treat button style as semantic emphasis:

- `primary`: main next action;
- `success`: affirmative/complete/pay/continue when semantically appropriate;
- `danger`: destructive or risky action;
- `link`: callback rendered with link-like treatment; Telegram restricts it to callback buttons.

Keep labels short. A useful rule of thumb is one dominant action plus a small number of secondary actions.

Do not encode authorization in button appearance. Every callback must be authorized server-side when received.

## Tables and dense data

Tables are best for short comparable fields, totals, inventory, invoices, and status matrices.

Recommended mobile layout:

- 2-4 columns for most cards;
- short headers;
- right-align numbers where it improves scanning;
- use `compact` for dense data;
- move descriptions into `details` rather than widening the table.

Telegram allows up to 20 columns, but the documented maximum is not a design target.

## Media-first cards

For products or visual entities:

```text
heading
-> slideshow/collage
-> one-sentence description
-> compact specs table
-> primary actions
```

Use slideshow when viewing items sequentially makes sense; use collage when simultaneous overview matters. Keep captions meaningful without depending on a particular client animation.

## Edit in place

Treat a bot message used as a card/menu/screen as a stable UI surface. Store its `message_id` and update that surface in place whenever Telegram exposes a supported edit method.

Recommended routing:

```text
text/rich content change -> editMessageText
media or hero image change -> editMessageMedia
caption-only change -> editMessageCaption
inline-keyboard-only change -> editMessageReplyMarkup
```

This keeps navigation visually stable, avoids chat clutter/flicker, and prevents callbacks from being unnecessarily rebound to a new message.

Delete-and-resend is appropriate only when the target message is no longer editable, Telegram does not document the required type transition, or product semantics intentionally require a new history item. If replacement is necessary, update stored message identifiers and callback/session state as one logical transaction.

Do not infer unsupported reverse conversions. In particular, the current Bot API explicitly documents text/rich-to-media through `editMessageMedia`; it does not document a general conventional-media-to-text-only conversion through `editMessageText`.

## Details and progressive disclosure

Use `<details><summary>...</summary>...</details>` for:

- help text;
- policy/terms summaries;
- technical metadata;
- secondary order details;
- diagnostic information.

Put the decision-critical content outside the disclosure. Users should not need to expand details to discover the primary price, state, warning, or action.

## Persian and RTL

For Persian/Arabic interfaces:

- set `is_rtl: true` explicitly when RTL is a product requirement;
- keep human-readable Persian labels concise;
- isolate long Latin IDs, URLs, SKU values, and tracking codes with `code` or separate cells where useful;
- do not manually reverse application data to imitate RTL;
- test mixed Persian/Latin content on representative Telegram clients.

Example final payload shape:

```json
{
  "html": "<h3>وضعیت سفارش</h3><p>سفارش شما آماده ارسال است.</p>",
  "is_rtl": true
}
```

See `assets/templates/persian-rtl-dashboard.html` for a reusable pattern.

## Loading and AI generation

Loading UI should be simpler than final UI.

Recommended sequence:

```text
short tg-thinking draft
-> occasional meaningful phase update
-> persistent final rich message
```

Do not stream every token merely to create motion. Coalesce updates, respect rate-limit responses, and make the final message understandable even if the user never saw a draft update.

## Mini App handoff

Use a rich `web_app` button only in the documented context (private chat, and not on behalf of a business account).

A Mini App is a good handoff for:

- multi-step forms;
- visual pickers;
- complex carts/configurators;
- dashboards requiring frequent local interaction.

Use an HTTPS URL from your expected/configured Mini App origin. Telegram has tightened Mini App origin security; do not design flows that rely on arbitrary alternate origins.

## Accessibility and fallback

- Give custom emoji meaningful Unicode alternatives.
- Do not use color/style as the only carrier of meaning.
- Keep action labels understandable as text.
- Produce an explicit plain-text fallback when legacy compatibility is a product requirement.
- Keep important data in text, not only in images.

## Reusable component model

For production bots, render UI from structured application data rather than concatenating arbitrary strings everywhere.

Example conceptual model:

```text
OrderCard
  title
  status
  rows[]
  total
  primaryAction
  secondaryActions[]
```

Then implement separate renderers:

```text
OrderCard -> InputRichMessage
OrderCard -> plain-text fallback
```

This makes escaping, tests, and design consistency easier and avoids trying to reverse rich HTML back into application state.

## Preflight checklist

Before shipping a polished card:

- primary information is visible without expansion;
- existing screen/card messages are edited in place when the desired transition is supported;
- one action is clearly dominant;
- button count is reasonable and each row remains within Telegram's 1-8 limit;
- table is narrow enough for mobile use;
- dynamic text/attributes are escaped;
- URLs are validated/allowlisted as required;
- callback state is opaque and authorized server-side;
- RTL is explicit where needed;
- custom emoji has fallback text;
- Mini App button is used only in a supported context;
- final content works without relying on undocumented client fallback behavior.
