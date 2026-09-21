# Rich buttons and colors

## Table of contents

- [Two placement modes](#two-placement-modes)
- [Button-row limit](#button-row-limit)
- [Actions](#actions)
- [Styles](#styles)
- [Action restrictions](#action-restrictions)
- [Rich buttons vs reply markup](#rich-buttons-vs-reply-markup)
- [Security](#security)
- [Examples](#examples)
- [Callback handling](#callback-handling)

## Two placement modes

Telegram rich messages support:

1. inline `<tg-button>` elements within supported inline flow;
2. `<tg-button-row>` as a block containing a row of rich buttons.

Example:

```html
<p>
  License: <tg-button type="copy_text" text="ABC-123">Copy</tg-button>
</p>
<tg-button-row align="center">
  <tg-button type="callback_data" style="primary" data="plan:pro">Choose Pro</tg-button>
  <tg-button type="url" style="success" url="https://example.com/help">Help</tg-button>
</tg-button-row>
```

## Button-row limit

`InputRichBlockButtons` contains 1-8 buttons. `align` can be `left`, `center`, or `right`.

Validate this before sending dynamic button arrays.

## Actions

A `RichMessageButton` contains text/style plus exactly one action. Telegram Bot API 10.3 documents these rich-button actions:

| Action | Main data |
| --- | --- |
| URL | `url` |
| callback | `callback_data` |
| Mini App | `web_app` |
| Telegram Login | `login_url` |
| switch inline query | `switch_inline_query` |
| switch inline in current chat | `switch_inline_query_current_chat` |
| choose target chat for inline query | `switch_inline_query_chosen_chat` |
| copy text | `copy_text` |
| disabled button | `disabled` |

In Rich HTML these are expressed through the documented `type` and related attributes.

## Styles

Documented semantic styles include:

- `primary`
- `success`
- `danger`
- `link`

`link` is restricted to callback buttons. Do not invent arbitrary hex colors; Telegram owns final theming and rendering.

## Action restrictions

### Callback data

`callback_data` must be 1-64 bytes. Count UTF-8 bytes, not JavaScript/Python character count.

Keep state identifiers short. Put large state in durable storage keyed by an opaque ID.

### Mini App

A rich `web_app` button is available for private chats. Telegram also documents that this action is not supported for messages sent on behalf of a Telegram Business account.

### Login URL

Use HTTPS. The bot/domain must be configured as required by Telegram login rules. Telegram Bot API 10.3 states that `login_url` is not supported for ephemeral messages.

Do not substitute a regular `url` action when an authenticated Login URL flow is required.

### Switch inline query

Telegram documents additional context restrictions:

- `switch_inline_query` is not supported in channel direct-message chats or for messages sent on behalf of a business account.
- `switch_inline_query_current_chat` is not supported in channels, channel direct-message chats, or messages sent on behalf of a business account.
- `switch_inline_query_chosen_chat` is not supported in channel direct-message chats or for messages sent on behalf of a business account.

For chosen-chat switching, set only the documented chat-type filters your product requires. Avoid requesting every destination type by default.

### Disabled

Use disabled buttons for non-interactive state. Do not attach another action field to a disabled button.

## Rich buttons vs reply markup

Use rich buttons when the interaction is part of the rich document itself. Use ordinary `InlineKeyboardMarkup` when the keyboard is conceptually separate, must remain compatible with ordinary messages, or existing framework logic is already based on reply markup.

A rich message may also have ordinary `reply_markup`; do not duplicate the same action in both surfaces without a product reason.

## Security

- Treat callback data as untrusted input when it comes back.
- Authorize the user/session on every state-changing callback.
- Do not put secrets or privileged state in callback data.
- Allowlist URL schemes and, where appropriate, hosts.
- Escape button text and attribute values.
- Keep Login URL destinations on configured/expected domains.
- Acknowledge callback queries promptly so the client does not keep showing a spinner.

## Examples

### URL and callback

```html
<tg-button-row align="center">
  <tg-button type="url" style="success" url="https://example.com/checkout">Checkout</tg-button>
  <tg-button type="callback_data" style="primary" data="cart:refresh">Refresh</tg-button>
</tg-button-row>
```

### Telegram Login

```html
<tg-button-row align="center">
  <tg-button type="login_url" url="https://auth.example.com/telegram">Sign in</tg-button>
</tg-button-row>
```

### Copy text

```html
<p>
  Tracking code: <code>TRK-42</code>
  <tg-button type="copy_text" text="TRK-42">Copy</tg-button>
</p>
```

### Chosen chat inline query

```html
<tg-button-row>
  <tg-button
    type="switch_inline_query_chosen_chat"
    query="catalog"
    allow-user-chats
    allow-group-chats>Share catalog</tg-button>
</tg-button-row>
```

## Callback handling

Application flow:

1. receive callback query;
2. validate/authorize payload;
3. answer callback query promptly;
4. update application state;
5. optionally call `editMessageText` with `rich_message` to replace the UI.

Do not call a nonexistent `editRichMessageText` Telegram method.
