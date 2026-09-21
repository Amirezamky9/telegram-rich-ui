# Premium Custom Emoji Registry

This directory is the machine-readable custom-emoji layer for the Telegram Rich UI skill.

## Files

- `catalog.json` — normalized registry, unique by `custom_emoji_id`.
- `catalog.csv` — spreadsheet-friendly view of the same registry.
- `curated-ui.json` — small style-consistent sets for agents building bot UI.
- `regional-packs.json` — Persian/Iranian discovery and enrichment state.
- `sources.json` — source provenance and reviewed snapshots.

## Safety model

Records with `selectable: true` have a fallback emoji and can be used by agents.
Records with `selectable: false` are inventory only. They must be enriched from Telegram with
`Sticker.emoji` before use, because Telegram requires a valid alternative emoji.

The primary dedupe key is `custom_emoji_id`. Duplicate source rows become aliases/keywords instead
of additional records.

Use `python3 scripts/search_emoji.py QUERY` to search and
`python3 scripts/validate_emoji_catalog.py` to validate integrity.
