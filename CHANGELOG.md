# Changelog

## 1.4.0 - 2026-09-22

- Added an explicit edit-in-place-first policy for Telegram bot UI screens.
- Added `editMessageMedia` guidance for media-to-media edits and text/rich-to-media transitions, including album, inline-message, and business-message restrictions.
- Added `editMessageCaption` and `editMessageReplyMarkup` routing so caption- or keyboard-only changes do not trigger delete-and-resend.
- Added aiogram 3.31+ and grammY 1.46+ media-edit recipes.
- Added UI guidance that treats delete-and-resend as a fallback only when Telegram has no supported edit path or the message is no longer editable.

## 1.3.0 - 2026-09-21

- Added a deduplicated Premium Custom Emoji Registry with **1,483 unique IDs**, JSON and CSV views.
- Added curated style-consistent UI sets for navigation, status, commerce, AI/tech, news/metrics, and Persian/Iranian cultural UI.
- Added Persian/Iranian custom-emoji pack inventory with 178 raw `iranNewz` IDs kept in a safe pending-enrichment state, plus discovered `Emojiran` and `Iranianflaghistory` packs.
- Added ranked semantic/Persian registry search, CSV sync validation, Bot API enrichment, custom-emoji pack import, deterministic export, and search regression tests.
- Added agent policy to prefer premium custom emoji for major UI cues while avoiding visual clutter.
- Added support guidance for custom emoji inside rich text and as keyboard button icons.
- Added duplicate-ID guards and non-selectable state for entries without verified fallback emoji.


## 1.2.0 - 2026-09-21

- Rebuilt `SKILL.md` as a portable control plane with standard frontmatter.
- Added `agents/openai.yaml` and moved Hermes-specific metadata to `metadata/hermes.yaml`.
- Re-audited Telegram Bot API 10.3 against the official documentation.
- Corrected edit semantics to `editMessageText` with `rich_message`.
- Corrected JSON table schema to use `cells` instead of `rows`.
- Added native-first aiogram 3.31.0 guidance and starter.
- Added native-first grammY 1.46.0 guidance and Cloudflare Worker starter.
- Added dedicated ephemeral-message and compatibility references.
- Rewrote streaming guidance to avoid unsupported rate-limit guarantees.
- Added deterministic validation, safe legacy fallback, fixtures, and CI.
- Added README and MIT license.

## 1.1.0

- Added Bot API 10.3 coverage and thinking/draft references.

## 1.0.0

- Initial repository release.
