# Thinking drafts and streaming

## Table of contents

- [Two draft methods](#two-draft-methods)
- [sendRichMessageDraft contract](#sendrichmessagedraft-contract)
- [tg-thinking](#tg-thinking)
- [Draft identifiers](#draft-identifiers)
- [Thirty-second preview](#thirty-second-preview)
- [Stop generation](#stop-generation)
- [Finalization](#finalization)
- [Rate limits and cadence](#rate-limits-and-cadence)
- [Cancellation architecture](#cancellation-architecture)
- [aiogram pattern](#aiogram-pattern)
- [grammY pattern](#grammy-pattern)
- [Failure handling](#failure-handling)

## Two draft methods

Telegram provides:

- `sendMessageDraft` for temporary plain-text generation previews;
- `sendRichMessageDraft` for temporary rich previews.

Both are intended for private-chat generation workflows and return `True` on success rather than a persistent message object.

For `sendMessageDraft`, Telegram permits an empty `text` value, which displays a native "Thinking..." placeholder.

## sendRichMessageDraft contract

Key fields:

- `chat_id`: integer identifier of the target private chat;
- `draft_id`: non-zero integer;
- `rich_message`: partial `InputRichMessage`;
- `message_thread_id`: optional;
- `can_stop`: optional;
- `keep_on_stop`: optional.

Telegram documents that changes made with the same `draft_id` can be animated; using a different identifier replaces the draft without the same continuation semantics.

Direct upload of new files and explicit file upload by URL are not supported in the draft method.

## tg-thinking

`<tg-thinking>` is a draft-only rich block. Telegram states that it may be used only in `sendRichMessageDraft`, so it cannot be received as a normal persisted message block.

Example:

```html
<tg-thinking>
  <tg-emoji emoji-id="5368324170671202286">🧠</tg-emoji>
  Checking data...
</tg-thinking>
```

Do not include `<tg-thinking>` in the final `sendRichMessage` payload.

The AIActions pack is linked by Telegram as a source of recommended custom emoji examples for this block.

## Draft identifiers

Generate a non-zero integer per active generation session.

Project recommendation:

- keep `(chat_id, draft_id)` mapped to the upstream generation task;
- avoid reusing a completed session ID for unrelated work;
- if you support concurrent generations in one private chat, allocate distinct IDs and maintain explicit ownership.

The allocation strategy is application-defined.

## Thirty-second preview

Telegram describes a draft as a temporary 30-second preview. It is not durable chat history.

Design implications:

- an application that runs longer than the preview window may update the draft while work continues;
- final persistence still requires `sendRichMessage` (or `sendMessage` for plain text);
- never treat `keep_on_stop` as permanent storage.

Do not claim that refreshing at one exact interval is mandated by Telegram. Choose a cadence appropriate to user experience and rate limits.

## Stop generation

When `can_stop: true`, the user can request generation to stop. Telegram then sends an update whose `stopped_message_generation` field is a `MessageGenerationStopped` object.

Documented fields:

- `chat`
- optional `message_thread_id`
- `draft_id`

Use `draft_id` plus chat identity to cancel the correct upstream task.

If `keep_on_stop: true`, Telegram keeps the draft temporarily, but it can still disappear after a short time or when the bot sends another message. To preserve partial output, send it as a new persistent message.

## Finalization

Successful lifecycle:

```text
user request
  -> allocate draft_id
  -> send/update temporary draft
  -> generation completes
  -> remove draft-only constructs from final content
  -> sendRichMessage(final rich_message)
  -> release task/session state
```

Do not assume sending an arbitrary final message edits a persistent draft object; the draft is a temporary preview and persistence is a separate send operation.

## Rate limits and cadence

Telegram does **not** document a magic interval that guarantees drafts will never receive HTTP 429.

Project recommendation:

- coalesce token-level updates into meaningful UI updates instead of sending every token;
- start with a human-readable cadence (for example, phase changes or several updates per second at most) and tune from telemetry;
- if Telegram returns a rate-limit response, honor documented retry information and use backoff;
- make the final persistent send independent from a missed intermediate update.

Never document "300 ms means no 429" as a Telegram guarantee.

## Cancellation architecture

Upstream work should be cancelable.

Recommended state model:

```text
(chat_id, draft_id)
  -> generation task / AbortController
  -> latest safe partial content
  -> finalization state
```

On `stopped_message_generation`:

1. find the active task;
2. cancel/abort upstream model or I/O work;
3. stop scheduling draft updates;
4. if your product needs durable partial output, send an explicit final message;
5. clear the session mapping.

Make cancellation idempotent; duplicate/retried updates must not corrupt unrelated sessions.

## aiogram pattern

aiogram 3.31.0 exposes native draft support:

```python
from aiogram.types import InputRichMessage

await bot.send_rich_message_draft(
    chat_id=chat_id,
    draft_id=draft_id,
    rich_message=InputRichMessage(
        html="<tg-thinking>Analyzing...</tg-thinking>"
    ),
    can_stop=True,
    keep_on_stop=True,
)

await bot.send_rich_message(
    chat_id=chat_id,
    rich_message=InputRichMessage(html="<p>Done.</p>"),
)
```

Use the typed `stopped_message_generation` update exposed by the current aiogram release to cancel your task.

## grammY pattern

grammY 1.46.0 exposes native Bot API methods:

```ts
await ctx.api.sendRichMessageDraft(ctx.chat.id, draftId, {
  html: "<tg-thinking>Analyzing...</tg-thinking>",
}, { can_stop: true, keep_on_stop: true });

await ctx.api.sendRichMessage(ctx.chat.id, {
  html: "<p>Done.</p>",
});
```

Use grammY's typed update/context facilities from the installed version. Avoid `as any` unless a newer Telegram field truly has not reached the framework yet.

## Failure handling

Classify failures:

- invalid rich markup/schema -> fix code/content; do not hide it with blind fallback;
- rate limit -> retry after documented delay/backoff;
- cancellation -> terminate upstream work;
- network/transient transport -> bounded retry if idempotency is safe;
- unsupported media in draft -> redesign the draft, then put media in the final persistent message.

Always make the final result understandable even if intermediate draft updates were skipped.
