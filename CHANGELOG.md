# Changelog

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
