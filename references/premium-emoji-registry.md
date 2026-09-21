# Premium Emoji Registry

## Table of contents

- [Purpose](#purpose)
- [Agent selection policy](#agent-selection-policy)
- [Registry files](#registry-files)
- [Text and Rich Message usage](#text-and-rich-message-usage)
- [Button usage](#button-usage)
- [Search workflow](#search-workflow)
- [Curated UI sets](#curated-ui-sets)
- [Persian and Iranian coverage](#persian-and-iranian-coverage)
- [Import and enrichment](#import-and-enrichment)
- [Deduplication policy](#deduplication-policy)
- [Safety and quality rules](#safety-and-quality-rules)
- [Source provenance](#source-provenance)

## Purpose

Use the Premium Emoji Registry whenever a Telegram bot UI benefits from semantic icons. For polished bot UI, prefer a suitable verified custom emoji over a plain Unicode decorative emoji when the bot is eligible and the richer icon improves navigation, status scanning, commerce, AI state, support, or branding.

Do not decorate every line. Premium emoji are a UI primitive, not confetti.

## Agent selection policy

1. Search the local registry before hard-coding an emoji ID.
2. Prefer records where `selectable=true`.
3. Prefer one coherent `style_family` inside the same card/menu.
4. Prefer curated sets for navigation, status, commerce, AI/tech, metrics, and Persian/Iranian surfaces.
5. Use the stored Unicode `fallback` inside every `<tg-emoji>` entity.
6. Never auto-select a `needs_enrichment` record.
7. If no suitable ready record exists, import/enrich a `t.me/addemoji/...` pack from Telegram.
8. Re-run `scripts/export_emoji_catalog.py` and `scripts/validate_emoji_catalog.py` after catalog changes.

## Registry files

`assets/emoji-catalog/catalog.json`
: Canonical machine-readable registry. The primary key is `custom_emoji_id`.

`assets/emoji-catalog/catalog.csv`
: Spreadsheet-friendly export of the same registry.

`assets/emoji-catalog/curated-ui.json`
: Small, intentionally selected groups for common bot UI surfaces.

`assets/emoji-catalog/regional-packs.json`
: Persian/Iranian regional discovery metadata and raw ID inventory.

`assets/emoji-catalog/sources.json`
: Source provenance and reviewed snapshots.

Current reviewed snapshot: **1,483 unique IDs**, **1,305 ready/selectable**, **178 pending enrichment**.

## Text and Rich Message usage

Rich HTML:

```html
<tg-emoji emoji-id="5877260593903177342">⚙️</tg-emoji> Settings
```

Use the registry's stored fallback. Do not invent one.

Rich Markdown can use Telegram's custom emoji image syntax where appropriate. For JSON blocks/rich text, use the framework-native custom emoji rich-text type.

## Button usage

Telegram has two distinct button models.

### RichMessageButton

A Rich Message button stores a `RichText` label. Telegram permits custom emoji inside that rich text.

```html
<tg-button-row align="center">
  <tg-button type="callback_data" style="primary" data="settings">
    <tg-emoji emoji-id="5877260593903177342">⚙️</tg-emoji> Settings
  </tg-button>
</tg-button-row>
```

### InlineKeyboardButton and KeyboardButton

Bot API 9.4+ exposes `icon_custom_emoji_id` on ordinary inline/reply keyboard buttons when the bot is eligible to use custom emoji.

Conceptual JSON:

```json
{
  "text": "Settings",
  "icon_custom_emoji_id": "5877260593903177342",
  "callback_data": "settings"
}
```

Do not prepend a plain Unicode decorative icon to the label when a suitable premium keyboard icon is already being supplied, unless the product intentionally wants both.

## Search workflow

```bash
python3 scripts/search_emoji.py settings
python3 scripts/search_emoji.py تنظیمات --limit 8
python3 scripts/search_emoji.py پرداخت --tag commerce
python3 scripts/search_emoji.py --curated minimal_navigation
python3 scripts/search_emoji.py iran --tag persian_ui --format html
python3 scripts/search_emoji.py --curated commerce --format id
```

Output formats:

- `table` — human/agent scanning;
- `json` — automation;
- `html` — ready-to-paste `<tg-emoji>` snippets;
- `id` — useful for `icon_custom_emoji_id`.

## Curated UI sets

The curated registry includes:

- `minimal_navigation` — settings, search, copy, trash, profile, support, links, navigation, updates, verification.
- `status_alerts` — success, warning, error, information, notification, verification, attention.
- `commerce` — wallet, card, shop, discount, price/payment.
- `ai_tech` — bot/AI, ChatGPT, Claude, Gemini, GitHub, Python, Docker, terminal.
- `news_metrics` — breaking, urgent, statistics, chart up/down, announcements.
- `iran_culture` — verified-fallback Iranian/Persian-friendly visual vocabulary such as Iran flag, watermelon/Yalda, sprouts/Nowruz, flowers, tea/coffee, celebration, heart.

Curated sets are deliberately small. Do not add near-duplicates just to increase count.

## Persian and Iranian coverage

Two layers are kept separate:

1. **Ready Persian/Iranian palette** — records with known fallback values and `persian_ui`/`iran_culture_palette` tags. These are safe for automatic selection.
2. **Regional raw inventory** — custom emoji IDs from Persian/Iranian packs such as `iranNewz`. IDs without verified `Sticker.emoji` remain `needs_enrichment` and `selectable=false`.

Discovered custom emoji packs:

- `https://t.me/addemoji/iranNewz`
- `https://t.me/addemoji/Emojiran`
- `https://t.me/addemoji/Iranianflaghistory`

Regular `t.me/addstickers/...` packs are ordinary sticker packs and are intentionally excluded from the custom-emoji registry.

## Import and enrichment

Import a whole custom emoji pack:

```bash
export BOT_TOKEN='...'
python3 scripts/import_emoji_pack.py https://t.me/addemoji/Emojiran \
  --category regional_iran --style-family Emojiran --tag iran --tag persian --write
python3 scripts/export_emoji_catalog.py
python3 scripts/validate_emoji_catalog.py
```

Enrich known pending IDs via `getCustomEmojiStickers`:

```bash
BOT_TOKEN=... python3 scripts/enrich_custom_emoji.py --write
python3 scripts/export_emoji_catalog.py
python3 scripts/validate_emoji_catalog.py
```

The importer verifies `sticker_type=custom_emoji`, extracts `custom_emoji_id`, uses Telegram's `Sticker.emoji` as fallback when available, and merges by ID.

## Deduplication policy

Invariant:

```text
one custom_emoji_id -> one catalog record
```

If the same ID appears from multiple sources/packs:

- keep one record;
- merge packs, aliases, keywords, tags and sources;
- keep one canonical fallback;
- do not create a duplicate merely because the source uses a different semantic key.

Near-duplicate visuals with **different Telegram IDs** remain distinct Telegram assets. Curated sets prevent agents from being overwhelmed by near-identical variants.

## Safety and quality rules

- Never generate UI from `selectable=false` records.
- Never invent a fallback for a missing `Sticker.emoji`.
- Follow current Telegram eligibility rules for chat type and bot owner/account status.
- Keep meaningful text labels for critical/destructive actions; iconography is not enough.
- Prefer a consistent style family inside a card/menu.
- Keep custom emoji usage restrained and semantic.
- Revalidate stored IDs periodically; packs/assets can evolve.
- For production-critical UI, send a canary in the actual target chat type.

## Source provenance

Exact source snapshots are in `assets/emoji-catalog/sources.json`.

Major inputs:

- Telegram official Bot API and custom emoji documentation.
- `Zulut30/premium-telegram-emoji` for catalogued IDs, fallbacks, semantic keys and pack references.
- MIT-licensed `uuigww/telegram_emoji_for_llm` for broad Unicode-fallback-to-custom-ID mapping.
- public Telegram custom emoji indexes for Persian/Iranian pack discovery and raw `iranNewz` IDs.
- `ehub.tg` as optional external discovery; no unreviewed bulk export from it is bundled.

The canonical registry stores normalized factual identifiers and project-authored metadata; source prose is not copied.
