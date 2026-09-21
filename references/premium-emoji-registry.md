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
- [Metadata and verification contract](#metadata-and-verification-contract)
- [Agent implementation recipes](#agent-implementation-recipes)

## Purpose

Use the Premium Emoji Registry whenever a Telegram bot UI benefits from semantic icons. For polished bot UI, prefer a suitable source-mapped custom emoji over a plain Unicode decorative emoji when the bot is eligible and the richer icon improves navigation, status scanning, commerce, AI state, support, or branding.

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

Current reviewed snapshot: **1,483 unique IDs**, **1,300 ready/selectable**, **183 pending enrichment** (178 regional IDs plus five invalid source fallbacks).

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
- `iran_culture` — source-mapped Iranian/Persian-friendly visual vocabulary such as Iran flag, watermelon/Yalda, sprouts/Nowruz, flowers, tea/coffee, celebration, heart.

Curated sets are deliberately small. Do not add near-duplicates just to increase count.

## Persian and Iranian coverage

Two layers are kept separate:

1. **Ready Persian/Iranian palette** — records with known fallback values and `persian_ui`/`iran_culture_palette` tags. These are eligible for selection, not proof of live delivery, visual appearance, or Iranian authorship.
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

## Metadata and verification contract

Read `references/curated-emoji-guide.md` for all 47 unique curated choices, grouped by UI use.
Read `references/emoji-registry-audit.md` for the reviewed snapshot and outstanding limitations.

- `category` preserves the upstream grouping; `ui_category` is the curated semantic grouping.
- `description`, `label_fa`, `description_fa`, and `usage_notes` are project-authored. Labels and descriptions are not claims about unseen artwork.
- `style_family` is source-derived. `style_policy` identifies mixed sets; a curated set is not necessarily a visually matching pack. `curation.visual_reviewed=false` explicitly records that distinction.
- `sources` resolve to `sources.json`. `provenance` records individual source locators, observed fallbacks, aliases and pack associations without overwriting earlier evidence.
- `verification.status=source_mapped` means the ID/fallback pair matches a recorded third-party snapshot, not Telegram runtime validation.
- `bot_api_verified` requires `checked_at` and the official method used. It verifies metadata at that time, not delivery eligibility or visual suitability.
- `pending` and `not_returned` are never UI-selectable. A successful response omitting an ID disables it; a request failure leaves files untouched.
- A plain symbol such as `%` or `₽` is not a verified emoji fallback. Preserve it in provenance and enrich the ID rather than inventing an alternative.

All IDs are decimal **strings**, including in TypeScript. Import the CSV ID column as Text; spreadsheet numeric inference can irreversibly round 19-digit IDs. JSON is canonical. CSV stores provenance/verification objects as JSON cells and is a generated export, not an import format.

Import/enrichment defaults to dry run. Use `--write` to save, then export and validate. The importer merges repeated IDs and preserves existing descriptions, aliases and tags; new IDs still need semantic curation. `--source-id` must reference an existing source. Official observations override the fallback, retaining earlier source observations. The regional pack file is historical discovery inventory, not a live pending-count report.

```bash
python3 scripts/search_emoji.py 'پشتیبانی' --curated minimal_navigation --format json
python3 scripts/search_emoji.py --ui-category commerce --style minimal_bw --format json
python3 scripts/search_emoji.py 5884510167986343350 --format json
python3 scripts/search_emoji.py --verified-only --format json
python3 scripts/search_emoji.py --include-unverified --format json
```

The last command is for inspection only. `--include-unverified` is rejected with `html`, `id`, or `button-json`; `--verified-only` can correctly return an empty list before official enrichment. Persian search normalizes Arabic ی/ک equivalents, vowel marks and half-spaces. Read `usage_notes` before choosing an icon. `button-json` emits an icon-field fragment, not a complete button.

## Agent implementation recipes

Retrieve a selectable record as JSON, and keep its ID/fallback together. Example TypeScript for grammY/Workers using a selected record:

```ts
const icon = { custom_emoji_id: "5884510167986343350", fallback: "💬" };
const escapeHtml = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const label = "پشتیبانی";
const html = `<tg-emoji emoji-id="${icon.custom_emoji_id}">${escapeHtml(icon.fallback)}</tg-emoji> ${escapeHtml(label)}`;
// sendMessage: pass html with parse_mode: "HTML".
// sendRichMessage: pass rich_message: { html: `<p>${html}</p>` }.
const inlineButton = { text: label, icon_custom_emoji_id: icon.custom_emoji_id, callback_data: "support" };
const replyButton = { text: label, icon_custom_emoji_id: icon.custom_emoji_id };
const richButton = {
  text: [{ type: "custom_emoji", custom_emoji_id: icon.custom_emoji_id, alternative_text: icon.fallback }, ` ${label}`],
  callback_data: "support",
};
```

Select only validated decimal-string IDs before inserting them into an HTML attribute. Keep dynamic text escaped. Place `inlineButton` inside `reply_markup.inline_keyboard`, `replyButton` inside `reply_markup.keyboard`, and `richButton` inside a rich button block. Acknowledge callback queries and implement the action separately.

For explicit `MessageEntity` arrays, measure offsets and lengths in UTF-16 code units (Python: `len(text.encode("utf-16-le")) // 2`), not code points. Prefer HTML when manual offsets are unnecessary. Never put `<tg-emoji>` markup into an ordinary keyboard's plain `text` field.

Do not assume the bot owner's Premium subscription enables channel posts or inline-mode results: check the destination and eligibility rules in the [official Bot API](https://core.telegram.org/bots/api#formatting-options). A delivery canary is separate from metadata enrichment. If custom emoji cannot be used, deliberately omit the keyboard icon and keep its label, or render the stored Unicode fallback in text.

Other surfaces have separate contracts: [forum-topic icons](https://core.telegram.org/bots/api#createforumtopic) require IDs from `getForumTopicIconStickers`; [custom reactions](https://core.telegram.org/bots/api#setmessagereaction) depend on message/chat permissions. A Mini App is web UI: an ID is not an image URL or a browser-renderable `<tg-emoji>`. Ordinary stickers require sticker file identifiers, not custom emoji IDs.
