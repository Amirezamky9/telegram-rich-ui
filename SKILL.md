---
name: telegram-rich-ui
description: Build, review, migrate, or troubleshoot Telegram Bot API 10.3 rich-message interfaces, including rich HTML/Markdown/blocks, tables, buttons, premium custom emoji, media, RTL, ephemeral messages, AI draft streaming, aiogram 3.31+, and grammY 1.46+ on Cloudflare Workers. Use when an agent must design polished Telegram bot UI, generate correct Bot API payloads, choose between native framework APIs and direct HTTP, validate rich-message schemas or limits, implement stop-aware streaming, or produce reliable legacy fallbacks without inventing unsupported Telegram behavior.
---

# Telegram Rich UI

Use this skill as a control plane. Load only the reference files needed for the current task. Treat Telegram's official Bot API as the source of truth; framework documentation maps that contract into aiogram or grammY.

## Required workflow

1. Identify the task: message design, tables, buttons, media, streaming, ephemeral delivery, aiogram, grammY/Cloudflare, migration, or debugging.
2. Read `references/SOURCES.md` before making version-sensitive claims.
3. Read `references/rich-formatting-overview.md` for the core message contract.
4. Read only the feature references that match the task.
5. For polished bot UI, search the Premium Emoji Registry and prefer a coherent custom-emoji set for major semantic UI cues; never use non-selectable registry records.
6. Prefer native framework APIs from the current supported versions documented here.
7. Generate payload/code.
8. Run `python3 scripts/validate_skill.py` after changing the skill itself.
9. For JSON `InputRichMessage` payloads, run `python3 scripts/validate_rich_message.py <file.json>` before shipping.
10. For user-supplied text, escape or structure it; never interpolate untrusted text into rich HTML attributes.
11. If a claim is not guaranteed by the official API, label it as a project recommendation or an empirical observation.

## Non-negotiable API rules

- Use `sendRichMessage` to persist a rich message.
- Edit a persistent rich message with `editMessageText` and its `rich_message` parameter. There is no Telegram method named `editRichMessageText`.
- `InputRichMessage` must contain exactly one of `html`, `markdown`, or `blocks`.
- Use `media` to bind media referenced from rich HTML or Markdown through Telegram `tg://...` identifiers.
- Rich messages are limited to 32,768 UTF-8 characters, 500 blocks, 16 nesting levels, 50 media attachments, and 20 table columns.
- A JSON table uses `cells`, a two-dimensional array. Never invent a top-level `rows` field for `InputRichBlockTable`.
- A button row contains 1-8 buttons.
- `callback_data` is 1-64 bytes.
- `web_app` rich buttons are for private chats and are not supported for messages sent on behalf of a Telegram Business account.
- `login_url` requires HTTPS and is not supported for ephemeral messages.
- `<tg-thinking>` is draft-only.
- `sendRichMessageDraft` targets a private chat, requires a non-zero `draft_id`, provides a temporary 30-second preview, and must be finalized with `sendRichMessage` when persistence is required.
- Draft rich messages do not support direct upload of new files or explicit upload by URL.
- Never promise a fixed draft update interval that prevents 429 responses. Back off on Telegram errors and follow `retry_after` when provided.
- Do not claim `getMe` can verify the human bot owner's Premium status. It returns bot identity/capability data, not the owner's subscription state.

## Format selection

Choose the simplest representation that preserves the requested UI:

- **Rich HTML:** default for hand-authored UI, templates, tables, buttons, media layout, RTL, and mixed content.
- **Rich Markdown:** use for document-like generated content that maps naturally to GitHub-Flavored Markdown plus supported rich HTML.
- **JSON blocks:** use when the application already has a typed component tree or needs machine validation without parsing HTML/Markdown.
- **Legacy `sendMessage`:** use when rich UI is unnecessary or when a deliberate legacy fallback is required.

Do not assume old clients will transform every rich construct in a specific way. If legacy behavior matters, explicitly generate a separate plain-text or legacy-HTML fallback.

## Reference router

| Need | Read |
| --- | --- |
| Core methods, limits, HTML/Markdown/blocks, edit semantics | `references/rich-formatting-overview.md` |
| Tables, cells, colspan/rowspan, JSON table schema | `references/tables-and-grids.md` |
| Rich buttons, actions, styles, restrictions | `references/rich-buttons-and-colors.md` |
| Slideshow, collage, embedded media, media identifiers | `references/slideshow-and-media.md` |
| Custom emoji rules and AIActions | `references/custom-emojis-and-stickers.md` |
| Premium emoji registry, semantic search, button icons, curated UI sets, Persian/Iranian packs | `references/premium-emoji-registry.md` |
| Draft lifecycle, stop handling, finalization | `references/thinking-drafts-and-streaming.md` |
| Ephemeral message parameters and edit/delete lifecycle | `references/ephemeral-messages.md` |
| Python implementation | `references/aiogram-python-recipes.md` |
| TypeScript + Cloudflare Workers implementation | `references/grammy-cloudflare-recipes.md` |
| Fallback and compatibility policy | `references/compatibility-and-fallbacks.md` |
| Polished card/menu/RTL/Mini App UI design patterns | `references/ui-design-patterns.md` |
| Version/source provenance | `references/SOURCES.md` |

## Premium Emoji Registry

- Search curated UI emoji first: `assets/emoji-catalog/curated-ui.json`.
- Search the full deduplicated registry with `python3 scripts/search_emoji.py QUERY`; use `--curated`, `--pack`, repeated `--tag`, and `--format id|html|json` when useful.
- Use only records with `selectable: true`; their fallback emoji is known.
- Prefer custom emoji in major status/navigation/payment/shop/AI/support cues instead of plain Unicode when a suitable premium entry exists.
- Keep one visual family per card when practical; premium does not mean visually noisy.
- For ordinary `InlineKeyboardButton`/`KeyboardButton`, use a selected ID as `icon_custom_emoji_id` where Telegram permits it. For `RichMessageButton`, put a custom-emoji rich-text entity inside the button label instead; these are different APIs.

## Reusable assets

- `assets/aiogram-starter/`: minimal aiogram 3.31+ starter.
- `assets/grammy-cloudflare-worker/`: Cloudflare Workers + grammY starter with webhook secret validation.
- `assets/templates/`: rich HTML examples, including a Persian RTL dashboard, suitable for adaptation after placeholder escaping.

## Deterministic helpers

- `scripts/validate_skill.py`: repository/skill integrity and regression checks.
- `scripts/validate_rich_message.py`: structural preflight for JSON rich-message payloads.
- `scripts/legacy_fallback.py`: rich HTML to safe plain-text fallback.
- `scripts/thinking_draft_demo.py`: dependency-free Bot API draft/final lifecycle demo.
- `scripts/search_emoji.py`: semantic/curated search across the deduplicated premium emoji registry.
- `scripts/import_emoji_pack.py`: import a `t.me/addemoji/...` pack using official Bot API metadata.
- `scripts/enrich_custom_emoji.py`: enrich pending IDs with `getCustomEmojiStickers`.
- `scripts/export_emoji_catalog.py`: regenerate the spreadsheet-friendly CSV from canonical JSON.
- `scripts/validate_emoji_catalog.py`: dedupe, fallback, curated-set, regional, CSV, and semantic-search integrity checks.

## Security and reliability

- Keep bot tokens, webhook secrets, API keys, and bot-owner information out of source control.
- Use Telegram `secret_token` when setting a webhook and verify `X-Telegram-Bot-Api-Secret-Token`; grammY can perform this check through `webhookCallback` options.
- Acknowledge callback queries promptly.
- Keep callback payloads compact and store large state server-side.
- Escape dynamic text and attribute values separately.
- Validate URLs before inserting them into `url`, `web_app`, or `login_url` buttons.
- Do not silently downgrade every `400 Bad Request` to a fallback. Treat malformed payloads as defects; use fallback only for an intentional compatibility path or a narrowly classified capability failure.
- Respect `RetryAfter`/`retry_after` on rate-limit responses rather than relying on a magic streaming interval.

## Completion checklist

Before returning production code or committing changes:

- Confirm the source snapshot in `references/SOURCES.md` is still current.
- Confirm no invented Bot API methods or schema fields are present.
- Confirm exactly one rich content source is used.
- Confirm table width and button-row limits.
- Confirm private-chat restrictions for drafts and `web_app` buttons.
- Confirm stop-generation events cancel upstream work and that `keep_on_stop` is not mistaken for permanent persistence.
- Confirm untrusted data is escaped.
- If the UI uses semantic/decorative icons, confirm the agent searched the Premium Emoji Registry first, used only selectable records, preserved the stored fallback, and kept the visual family coherent.
- Confirm framework-native methods are used when supported.
- Run repository validation and, where practical, a Telegram canary against a test bot/chat.
