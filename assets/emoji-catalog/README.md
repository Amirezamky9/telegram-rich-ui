# Premium Custom Emoji Registry

This directory is the machine-readable custom-emoji layer for the Telegram Rich UI skill.

## Files

- `catalog.json` — canonical normalized registry, unique by `custom_emoji_id`.
- `catalog.csv` — spreadsheet-friendly export generated from the JSON registry.
- `curated-ui.json` — small style-aware sets for agents building bot UI.
- `regional-packs.json` — Persian/Iranian pack discovery plus raw-ID/enrichment state.
- `sources.json` — source provenance and reviewed snapshots.

## Safety model

- `selectable: true` means the record has a known fallback and may be auto-selected.
- `selectable: false` means inventory only; enrich it from Telegram before use.
- Primary dedupe key: `custom_emoji_id`.
- Duplicate source rows become aliases/keywords/source provenance rather than duplicate records.

## Search

```bash
python3 scripts/search_emoji.py settings
python3 scripts/search_emoji.py تنظیمات
python3 scripts/search_emoji.py --curated minimal_navigation
python3 scripts/search_emoji.py پرداخت --tag commerce --format html
```

## Maintain

```bash
python3 scripts/export_emoji_catalog.py
python3 scripts/validate_emoji_catalog.py
```

To import or enrich a pack, see `references/premium-emoji-registry.md`.
