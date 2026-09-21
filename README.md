# Telegram Rich UI

A source-grounded agent skill and implementation reference for Telegram Bot API 10.3 rich messages.

The repository is designed for both humans and coding agents. `SKILL.md` is intentionally a small control plane; detailed API contracts live under `references/`, deterministic checks live under `scripts/`, and runnable starters live under `assets/`.

## Verified compatibility snapshot

Verified on 2026-09-21 against:

- Telegram Bot API 10.3 (2026-08-24)
- aiogram 3.31.0
- grammY 1.46.0
- Cloudflare Workers webhook deployment model documented by grammY

See `references/SOURCES.md` for provenance and freshness rules.

## What this skill covers

- `sendRichMessage` with rich HTML, Rich Markdown, or JSON blocks
- `editMessageText` with `rich_message`
- tables, lists, quotations, details, math, anchors, localized time, RTL
- inline rich buttons and button rows
- collages, slideshows, embedded photo/video/audio/document media
- custom emoji and AIActions guidance
- deduplicated Premium Emoji Registry with semantic/Persian search, curated UI palettes, CSV export, and Bot API pack import/enrichment
- ephemeral messages
- `sendMessageDraft` and `sendRichMessageDraft`
- stop-generation handling via `stopped_message_generation`
- aiogram 3.31+ native APIs
- grammY 1.46+ native APIs
- Cloudflare Workers webhook deployment
- polished UI/RTL/Mini App handoff patterns
- deterministic schema/integrity checks and safe legacy fallback

## Repository layout

```text
.
├── SKILL.md
├── README.md
├── LICENSE
├── agents/
│   └── openai.yaml
├── metadata/
│   └── hermes.yaml
├── references/
│   ├── SOURCES.md
│   ├── rich-formatting-overview.md
│   ├── tables-and-grids.md
│   ├── rich-buttons-and-colors.md
│   ├── slideshow-and-media.md
│   ├── custom-emojis-and-stickers.md
│   ├── premium-emoji-registry.md
│   ├── thinking-drafts-and-streaming.md
│   ├── ephemeral-messages.md
│   ├── aiogram-python-recipes.md
│   ├── grammy-cloudflare-recipes.md
│   ├── compatibility-and-fallbacks.md
│   └── ui-design-patterns.md
├── scripts/
│   ├── validate_skill.py
│   ├── validate_rich_message.py
│   ├── legacy_fallback.py
│   └── thinking_draft_demo.py
├── assets/
│   ├── aiogram-starter/
│   ├── grammy-cloudflare-worker/
│   └── templates/
└── tests/fixtures/
```

## Fast start: aiogram

```bash
cd assets/aiogram-starter
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export BOT_TOKEN='...'
python main.py
```

The starter uses aiogram's native `InputRichMessage`, `send_rich_message`, and `send_rich_message_draft` APIs. It does not invent custom Telegram methods.

## Fast start: grammY on Cloudflare Workers

```bash
cd assets/grammy-cloudflare-worker
npm install
npx wrangler secret put BOT_TOKEN
npx wrangler secret put WEBHOOK_SECRET
npx wrangler secret put BOT_INFO
npm run deploy
```

Set `BOT_INFO` to the JSON `result` object returned by Telegram `getMe` (it is non-secret bot metadata), then set the Telegram webhook with the same secret token:

```bash
curl -sS -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
  -d "url=https://YOUR-WORKER.workers.dev/telegram" \
  -d "secret_token=${WEBHOOK_SECRET}"
```

The Worker uses grammY's native `ctx.api.sendRichMessage` and `ctx.api.sendRichMessageDraft` methods and delegates webhook secret checking to `webhookCallback`.

## Validate the skill

```bash
python3 scripts/validate_skill.py
```

The validator checks, among other regressions:

- required files and metadata
- valid two-key `SKILL.md` frontmatter
- broken local references
- missing TOCs in long reference files
- accidental reintroduction of the nonexistent `editRichMessageText` API name
- accidental use of a JSON table `rows` field instead of `cells`
- Python syntax
- fixtures for valid and invalid rich-message structures

Validate a JSON rich message:

```bash
python3 scripts/validate_rich_message.py tests/fixtures/valid-table.json
```

## Premium Emoji Registry

The skill includes a deduplicated custom-emoji registry under `assets/emoji-catalog/`.

Current reviewed snapshot:

- **1,483 unique** `custom_emoji_id` values;
- **1,300 ready/selectable** entries with a known Unicode fallback;
- **178 Persian/Iranian regional IDs** from `iranNewz` held as `needs_enrichment` until Telegram returns their official fallback metadata;
- curated UI sets for navigation, status, commerce, AI/tech, news/metrics, and Persian/Iranian cultural UI;
- `catalog.csv` for spreadsheet workflows.

Search:

```bash
python3 scripts/search_emoji.py settings
python3 scripts/search_emoji.py تنظیمات
python3 scripts/search_emoji.py پرداخت --tag commerce
python3 scripts/search_emoji.py --curated minimal_navigation
python3 scripts/search_emoji.py --curated commerce --format id
python3 scripts/search_emoji.py iran --tag persian_ui --format html
```

Maintain/import:

```bash
BOT_TOKEN=... python3 scripts/import_emoji_pack.py https://t.me/addemoji/Emojiran \
  --category regional_iran --style-family Emojiran --tag iran --tag persian --write
BOT_TOKEN=... python3 scripts/enrich_custom_emoji.py --write
python3 scripts/export_emoji_catalog.py
python3 scripts/validate_emoji_catalog.py
```

Agents are instructed to prefer suitable Premium custom emoji over plain decorative Unicode for polished UI when the bot is eligible, while keeping usage restrained and style-consistent.

For ordinary keyboard buttons use `icon_custom_emoji_id` where Telegram permits it. For `RichMessageButton`, custom emoji belong inside the RichText button label instead.

See `references/premium-emoji-registry.md`.

## Engineering policy

This repository separates three types of statement:

1. **Official contract**: guaranteed or specified by Telegram's Bot API documentation.
2. **Framework mapping**: behavior/types exposed by the documented aiogram or grammY release.
3. **Project recommendation**: an operational choice, such as coalescing stream updates or generating explicit legacy fallbacks.

Recommendations are never written as Telegram guarantees. Human-readable Bot API error descriptions are not treated as stable machine contracts.

## Important corrections from the pre-1.2 layout

- Replaced the invented `editRichMessageText` API name with `editMessageText(..., rich_message=...)`.
- Corrected JSON tables to use a two-dimensional `cells` array instead of `rows`.
- Removed claims that `getMe` can reveal the human bot owner's Premium subscription.
- Replaced string-replacement fallback logic with a real plain-text renderer.
- Removed guarantees that a fixed draft interval prevents 429 responses.
- Removed dead reference paths and added integrity checks.
- Switched aiogram and grammY guidance to native-first APIs.
- Added a maintained Cloudflare Worker starter and CI validation.

## License

MIT. See `LICENSE`.
