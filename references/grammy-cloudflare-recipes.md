# grammY 1.46+ on Cloudflare Workers

## Table of contents

- [Supported baseline](#supported-baseline)
- [Why grammY fits Workers](#why-grammy-fits-workers)
- [Project setup](#project-setup)
- [Worker lifecycle](#worker-lifecycle)
- [Webhook security](#webhook-security)
- [Send rich UI](#send-rich-ui)
- [Edit rich UI](#edit-rich-ui)
- [Edit media in place](#edit-media-in-place)
- [Draft streaming](#draft-streaming)
- [Stop generation](#stop-generation)
- [Building polished UI](#building-polished-ui)
- [Cloudflare state choices](#cloudflare-state-choices)
- [Deployment](#deployment)
- [Failure handling](#failure-handling)

## Supported baseline

Reviewed against:

- grammY 1.46.0
- Telegram Bot API 10.3 types exposed by grammY
- Wrangler 4.135.0
- grammY's documented Cloudflare Workers Node.js webhook pattern

Current grammY exposes native `sendRichMessage`, `sendRichMessageDraft`, and `sendMessageDraft`. Do not route normal calls through an untyped `raw` escape hatch on this baseline.

## Why grammY fits Workers

grammY supports webhook-driven serverless runtimes and documents Cloudflare Workers deployment. A Worker is a good fit for Telegram bots that:

- handle short webhook transactions;
- call external APIs;
- store state in external/Cloudflare services;
- render Telegram UI without requiring a permanently running process.

Do not run long polling inside a normal Cloudflare Worker request handler.

## Project setup

A complete starter is under `assets/grammy-cloudflare-worker/`.

Core dependencies:

```json
{
  "dependencies": {
    "grammy": "1.46.0"
  },
  "devDependencies": {
    "wrangler": "4.135.0"
  }
}
```

The official Node.js Worker pattern imports from `grammy`:

```ts
import { Bot, webhookCallback } from "grammy";
```

grammY also ships a web bundle for browser-like environments, but the documented Node.js Cloudflare Worker setup works with the package's normal import path.

## Worker lifecycle

Avoid a `getMe` call on every request. The official grammY Cloudflare Node.js pattern supplies known bot info to the `Bot` constructor.

Recommended environment:

```ts
interface Env {
  BOT_TOKEN: string;
  BOT_INFO: string;
  WEBHOOK_SECRET: string;
}
```

`BOT_INFO` is the JSON `result` object from Telegram `getMe` and is non-secret bot metadata. Keep `BOT_TOKEN` and `WEBHOOK_SECRET` as Worker secrets.

Construct the bot per request or cache safe module-level data as appropriate for Workers. Do not assume a Worker isolate is permanent.

## Webhook security

When calling `setWebhook`, provide Telegram's `secret_token`.

Then let grammY verify the `X-Telegram-Bot-Api-Secret-Token` header through `webhookCallback`:

```ts
return webhookCallback(bot, "cloudflare-mod", {
  secretToken: env.WEBHOOK_SECRET,
})(request);
```

Do not write a home-grown string comparison if grammY's adapter already supports the secret-token check.

Use a dedicated path such as `/telegram`; return 404/405 for unrelated requests.

## Send rich UI

`ctx.api.sendRichMessage` is typed in grammY 1.46.0:

```ts
await ctx.api.sendRichMessage(ctx.chat.id, {
  html: [
    "<h3>Order</h3>",
    "<p>Your order is ready.</p>",
    "<tg-button-row align=\"center\">",
    "<tg-button type=\"callback_data\" style=\"primary\" data=\"order:details\">Details</tg-button>",
    "</tg-button-row>",
  ].join(""),
});
```

No `as any` is needed for normal Bot API 10.3 rich-message calls on the reviewed version.

## Edit rich UI

grammY 1.46.0 accepts either a plain string or an `InputRichMessage` object as the third argument. An object maps to Telegram's `rich_message` parameter.

```ts
await ctx.api.editMessageText(chatId, messageId, {
  html: "<p><b>Updated</b></p>",
});
```

Inside a context for the message being edited, the corresponding context helper accepts the same string-or-rich-message content model. Let TypeScript/IDE autocomplete confirm optional arguments when upgrading grammY.

Never call an invented Telegram endpoint named `editRichMessageText`.

## Edit media in place

Use grammY's typed media builder and `editMessageMedia` for message-as-screen UIs instead of delete-and-resend:

```ts
import { InputMediaBuilder } from "grammy";

const media = InputMediaBuilder.photo(newPhotoFileId, {
  caption: "Updated product card",
});

await ctx.api.editMessageMedia(chatId, messageId, media, {
  reply_markup: updatedKeyboard,
});
```

The same Bot API method can replace a text or rich message with media. If only the caption changes, use `editMessageCaption`; if only the keyboard changes, use `editMessageReplyMarkup`.

When editing an inline message, do not upload a new file; use a Telegram `file_id` or URL. Preserve album-type constraints and the documented business-message edit window. Treat delete-and-resend as an explicit fallback for unsupported transitions or non-editable messages.

## Draft streaming

```ts
await ctx.api.sendRichMessageDraft(ctx.chat.id, draftId, {
  html: "<tg-thinking>Analyzing...</tg-thinking>",
}, {
  can_stop: true,
  keep_on_stop: true,
});

// ...cancelable work...

await ctx.api.sendRichMessage(ctx.chat.id, {
  html: "<p>Done.</p>",
});
```

Draft streaming is a private-chat feature. Keep `draftId` non-zero.

Do not attach a new direct upload or explicit URL upload to a rich draft. Put media in the final message if needed.

## Stop generation

The Telegram update includes `stopped_message_generation` with chat, optional thread ID, and draft ID.

For short Worker requests, durable generation often runs outside the initial webhook request (for example in a queue, Durable Object, or external model service). Cancellation therefore needs shared state, not only an in-memory map.

Recommended architecture:

```text
Telegram update
  -> Worker webhook
  -> durable job/session keyed by chat_id + draft_id
  -> abort/cancel flag or provider cancellation
```

A module-level `Map` is not durable across Worker isolate eviction and must not be your only cancellation state for long-running jobs.

## Building polished UI

For UI quality:

- build reusable render functions that return a complete `InputRichMessage` object;
- use semantic rich button styles rather than colors encoded in text;
- keep tables narrow and compact;
- use `details` for secondary information;
- use slideshow/collage for visual catalogs;
- use `tg-time` for recipient-localized dates;
- set `is_rtl` explicitly for Persian/Arabic UI;
- keep callback data short and store application state separately;
- make loading/draft UI visually simpler than the final result.

Example render function:

```ts
function renderOrder(order: { id: string; total: string }) {
  const id = escapeHtml(order.id);
  const total = escapeHtml(order.total);
  return {
    html: `<h3>Order ${id}</h3>` +
      `<table bordered compact>` +
      `<tr><th>Total</th><td align="right">${total}</td></tr>` +
      `</table>` +
      `<tg-button-row align="center">` +
      `<tg-button type="callback_data" style="primary" data="order:${id}">Details</tg-button>` +
      `</tg-button-row>`,
  };
}
```

If an identifier can contain arbitrary user input, do not copy it directly into callback data; map it to a validated opaque key.

### Escaping

```ts
function escapeHtml(value: unknown): string {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
```

Escaping does not replace URL validation or authorization.

## Cloudflare state choices

Choose state based on durability requirements:

- environment variables/secrets: configuration only;
- KV: read-heavy configuration/cache where eventual consistency is acceptable;
- D1: relational durable application data;
- Durable Objects: per-session/per-chat coordination and strongly coordinated state;
- Queues: deferred/long work and retries;
- external database/service: when already part of your architecture.

Do not hold durable order/session/generation state only in Worker memory.

## Deployment

Starter commands:

```bash
npm install
npx wrangler secret put BOT_TOKEN
npx wrangler secret put WEBHOOK_SECRET
npx wrangler secret put BOT_INFO
npm run deploy
```

Set `BOT_INFO` to the JSON `result` object from `getMe` (for example as a Worker secret/variable via your deployment system). Do not commit the bot token.

Set Telegram webhook with matching secret:

```bash
curl -sS -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
  -d "url=https://YOUR-WORKER.workers.dev/telegram" \
  -d "secret_token=${WEBHOOK_SECRET}"
```

After deployment, check `getWebhookInfo` and send a test update.

## Failure handling

- return a successful webhook response only after the update has been accepted for processing by your design;
- keep handlers within Worker execution constraints;
- move expensive/long tasks to an appropriate durable async path;
- use Telegram retry information on 429 responses;
- log request IDs/update IDs but never bot tokens;
- make handlers idempotent where Telegram/webhook retries can re-deliver work;
- treat invalid rich markup as a defect, not as a reason to silently cast to plain text.
