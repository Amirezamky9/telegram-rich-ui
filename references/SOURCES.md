# Source provenance and freshness policy

## Table of contents

- [Verified snapshot](#verified-snapshot)
- [Primary sources](#primary-sources)
- [Framework sources](#framework-sources)
- [GitHub implementation sources](#github-implementation-sources)
- [Freshness rules](#freshness-rules)
- [Claim policy](#claim-policy)

## Verified snapshot

Last reviewed: **2026-09-21**.

| Component | Reviewed version/state |
| --- | --- |
| Telegram Bot API | 10.3, released 2026-08-24 |
| aiogram | 3.31.0 |
| grammY | 1.46.0 |
| Cloudflare runtime pattern | grammY Cloudflare Workers Node.js documentation |

Always re-check these versions before updating version-sensitive examples.

## Primary sources

Telegram official documentation is authoritative for the API contract:

- Bot API: https://core.telegram.org/bots/api
- Bot API changelog: https://core.telegram.org/bots/api-changelog
- Bots features overview: https://core.telegram.org/bots/features

For rich messages, verify the live sections for:

- `InputRichMessage`
- `InputRichMessageMedia`
- `InputRichBlock*`
- `RichText*`
- `RichMessageButton`
- `sendRichMessage`
- `sendRichMessageDraft`
- `sendMessageDraft`
- `editMessageText`
- `EphemeralMessageParameters`
- `MessageGenerationStopped`
- rich-message formatting options

Do not promote an observed client rendering detail to API contract unless Telegram documents it.

## Framework sources

### aiogram

- Documentation: https://docs.aiogram.dev/en/latest/
- `SendRichMessage`: https://docs.aiogram.dev/en/latest/api/methods/send_rich_message.html
- `SendRichMessageDraft`: https://docs.aiogram.dev/en/latest/api/methods/send_rich_message_draft.html
- `InputRichMessage`: https://docs.aiogram.dev/en/latest/api/types/input_rich_message.html
- Changelog: https://docs.aiogram.dev/en/latest/changelog.html
- PyPI: https://pypi.org/project/aiogram/

The reviewed baseline is aiogram 3.31.0. Avoid aiogram 3.29.0: its changelog records a severe nested rich-block validation slowdown that was fixed in 3.29.1.

### grammY

- Documentation: https://grammy.dev/
- API reference: https://grammy.dev/ref/core/api
- `webhookCallback`: https://grammy.dev/ref/core/webhookcallback
- Cloudflare Workers Node.js: https://grammy.dev/hosting/cloudflare-workers-nodejs
- npm: https://www.npmjs.com/package/grammy

The reviewed baseline is grammY 1.46.0.

## GitHub implementation sources

Use source repositories as a secondary implementation check, not as a replacement for Telegram's official contract:

- aiogram: https://github.com/aiogram/aiogram
  - implementation snapshot reviewed at `97cfe79fa0ac9459d498bdb15cb7cb0530dbaac7`
  - native rich-message method implementations
  - tests under `tests/test_api/test_methods/`
- grammY: https://github.com/grammyjs/grammY
  - implementation snapshot reviewed at `055a5a440f04d0b9fd5fd75a6d14dac4c2b83553`
  - `src/core/api.ts`
  - `src/context.ts`
- grammY examples: https://github.com/grammyjs/examples

When a framework implementation and the official Telegram documentation disagree, treat Telegram as the API source of truth and then check whether the framework version is stale.

## Freshness rules

Re-run a source audit when any of the following changes:

1. Telegram announces a new Bot API version.
2. aiogram changes major/minor version or rich-message types.
3. grammY changes major/minor version or its Telegram type package.
4. Cloudflare changes Worker module/runtime requirements used by the starter.
5. A production request fails with a Telegram schema error that contradicts this repository.

For every refresh:

1. Read the Telegram changelog first.
2. Compare the relevant live API sections.
3. Check aiogram and grammY release notes/types.
4. Update this source snapshot.
5. Run `python3 scripts/validate_skill.py`.
6. Run a canary in a disposable Telegram test chat when credentials are available.

## Claim policy

Use these labels mentally and in documentation when ambiguity matters:

- **Official**: directly specified by Telegram.
- **Framework**: exposed by the reviewed aiogram/grammY version.
- **Recommendation**: this repository's engineering guidance.
- **Empirical**: observed in a client/runtime but not guaranteed by Telegram.

Never encode human-readable Telegram error `description` text as a stable programmatic contract. Telegram also notes that numeric `error_code` contents can change. Prefer framework-typed exceptions and documented `ResponseParameters` (for example retry information), and treat broad HTTP/error categories defensively rather than matching exact English sentences.


## Premium emoji registry sources

- Telegram Bot API custom emoji / Sticker metadata: authoritative runtime source for fallback `Sticker.emoji`, `custom_emoji_id`, `set_name`, and `needs_repainting`.
- `Zulut30/premium-telegram-emoji` snapshot `348ed01f497bab811c7f835c25b88aefa181fb78`: semantic keys, IDs, fallbacks, and pack references. The registry synthesizes its own descriptions instead of copying source prose.
- `uuigww/telegram_emoji_for_llm` snapshot `4e7043daf55a123fd37c5162e294d6ed01c92b74` (MIT): broad Unicode-to-custom-emoji mapping.
- Public Telegram indexes were used to discover/index Iranian custom-emoji packs, including `iranNewz`, `Emojiran`, and `Iranianflaghistory`. Raw regional IDs without Bot API fallback metadata remain non-selectable.
- `ehub.tg` is documented as an optional discovery/search surface, but was not bulk-imported because this review did not consume a stable bulk export.
