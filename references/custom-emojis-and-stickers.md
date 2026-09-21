# Custom emojis and stickers

## Table of contents

- [Custom emoji in rich messages](#custom-emoji-in-rich-messages)
- [Fallback text](#fallback-text)
- [Bot eligibility](#bot-eligibility)
- [What getMe can and cannot prove](#what-getme-can-and-cannot-prove)
- [Discovering emoji IDs](#discovering-emoji-ids)
- [AIActions](#aiactions)
- [Button icons](#button-icons)
- [Verification strategy](#verification-strategy)

## Custom emoji in rich messages

Use Telegram's custom emoji entity in Rich HTML:

```html
<tg-emoji emoji-id="5368324170671202286">👍</tg-emoji>
```

The `emoji-id` is the custom emoji identifier. The inner character/text is the fallback representation and must remain meaningful when the custom emoji cannot be displayed.

Rich Markdown can use Telegram's documented custom-emoji syntax as well; prefer HTML in UI templates when clarity matters.

## Fallback text

Always provide a sensible Unicode fallback. Do not use an empty placeholder simply because your primary test account displays the custom emoji.

Fallback behavior matters when:

- the client cannot display the custom emoji;
- a recipient lacks the capability required to render it;
- content is forwarded into a context with different emoji capabilities.

The exact animation/rendering remains client behavior.

## Bot eligibility

Telegram documents special bot rules for sending custom emoji. At the reviewed Bot API version, bots may use custom emoji in directly sent messages to private chats, groups, and supergroups when the bot owner has Telegram Premium. Telegram also documents an alternative eligibility path for bots with additional usernames purchased on Fragment.

Do not generalize this statement to unsupported chat types or contexts beyond the official rule.

## What getMe can and cannot prove

`getMe` verifies the bot token and returns information about the bot user and its bot capabilities.

It **does not expose the human owner's Telegram Premium subscription state**. Therefore:

- do not write code that calls `getMe` to infer owner Premium;
- do not treat the absence/presence of a `getMe` field as proof of the owner's subscription;
- verify custom-emoji sending with an actual canary when this capability is business-critical.

This corrects a common but invalid capability-check pattern.

## Discovering emoji IDs

Use documented Bot API methods/types for custom emoji sticker metadata, such as `getCustomEmojiStickers`, when you already know candidate custom emoji IDs.

Do not scrape UI internals or hard-code IDs without a provenance note when the exact asset matters.

Store selected IDs in configuration rather than scattering them through templates.

## AIActions

Telegram's rich-message documentation explicitly points to the AIActions custom emoji pack for examples recommended inside the draft-only `<tg-thinking>` block:

https://t.me/addemoji/AIActions

Use it as a visual enhancement, not as a dependency for the streaming protocol itself.

Example:

```html
<tg-thinking>
  <tg-emoji emoji-id="5368324170671202286">🧠</tg-emoji>
  Analyzing...
</tg-thinking>
```

The exact emoji ID in an example is not a promise that a particular visual asset will remain unchanged forever. Maintain application-selected IDs separately.

## Button icons

Telegram's ordinary keyboard/button types may expose `icon_custom_emoji_id` depending on the relevant Bot API object and framework version. That feature is separate from embedding `<tg-emoji>` inside rich text.

When using framework-generated types:

- prefer the framework field over building raw JSON;
- validate eligibility and fallback UI;
- do not assume a button icon changes the rich-button action contract.

## Verification strategy

For a feature that relies on custom emoji:

1. call `getMe` only to validate the bot token/identity;
2. send a canary message containing the desired custom emoji and a clear fallback;
3. inspect the result in representative recipient accounts/clients;
4. keep the fallback acceptable even if the custom asset is unavailable;
5. log API failures without logging the bot token.

Do not make owner-Premium verification a hidden prerequisite that the Bot API cannot actually inspect.
