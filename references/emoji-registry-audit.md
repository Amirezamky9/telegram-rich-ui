# Emoji registry audit — 2026-09-21

Scope: deeply curate existing UI sets; audit all catalog IDs, source mappings, deduplication and agent tooling. Starting branch commit: `44cffd125e719bf8773b6aa621437aa7ef6f7f04`.

## Findings and disposition

| Area | Evidence / result | Disposition |
| --- | --- | --- |
| Canonical uniqueness | 1,483 records, 1,483 unique decimal-string IDs | Preserve one canonical record per ID; shared set references are intentional |
| Curated selection | Six sets, 47 unique IDs | Added project-authored descriptions, Persian labels, semantic UI categories and per-entry cautions |
| Upstream mappings | All original 1,305 selectable ID/fallback pairs match the two recorded Git blobs | Store per-record source locators and original observations; classify as `source_mapped` |
| Unsafe fallbacks | `%`, `₽`, `…`, `⋮`, `#` were treated as valid alternative emoji | Quarantine five records, preserve source values in provenance; require official enrichment |
| Final selection | 1,300 selectable; 183 pending | Pending = 178 regional raw IDs + five source-symbol entries |
| Duplicate source observations | Keyboard ID `5877396173135811032` appears as `keyboard`/`klaviatura`, with `⌨️`/`⌨` | One record, aliases and both observations retained; original canonical fallback retained |
| Pack provenance | Explicit pack headers exist for NewsEmoji, logo_by_TgEmojiBot and TgAndroidIcons | Preserve those associations; do not inherit a header into an unrelated section |
| Visual coherence | Some curated sets mix source families; no asset previews inspected | Explicit per-set style policy and `visual_reviewed=false` |
| Pending output leakage | Inspection flag previously allowed raw ID/button output | Restrict pending inspection to table/JSON; ready output uses readiness checks |
| Import provenance | Default imported source IDs were not registered; merge retained stale fallback | Use registered official source; keep method/ID/pack observations; apply authoritative fallback |
| Revalidation | Missing IDs or missing fallback could leave previously ready records selectable | Mark them pending; preserve source evidence; request failures do not write files |
| Regional validation | Validator equated pack inventory length with pending count | Validate inventory membership independently of enrichment state |
| CSV drift | Validator checked only counts and IDs | Compare every generated CSV field, including provenance and verification |
| Persian selection | Arabic/Persian letter variants and half-spaces could differ | Normalize letters, vowel marks and half-spaces; add Persian labels to curated search |

## Source snapshots

The exact snapshots are linked in `assets/emoji-catalog/sources.json`:

- `Zulut30/premium-telegram-emoji`, upstream file **references/emoji-catalog.md**, Git blob `348ed01f497bab811c7f835c25b88aefa181fb78`.
- `uuigww/telegram_emoji_for_llm`, `data/restricted-emoji-map.json`, Git blob `4e7043daf55a123fd37c5162e294d6ed01c92b74`.

The audit compared identifiers and fallbacks, not copied source prose. Descriptions and cultural use suggestions are project-authored. Source metadata records an MIT claim/license; this audit does not independently establish ownership of every Telegram artwork. Source mapping is neither a content license nor a visual review.

## Persian / Iranian evidence

- Ten curated entries provide general country/cultural vocabulary (Iran flag, watermelon, seedling, flowers, hot drink, celebration, heart). Seasonal associations such as Yalda/Nowruz are editorial suggestions. They are not proof that the assets were designed by Iranian creators.
- The public [Emojiran page](https://t.me/addemoji/Emojiran) identifies “iRan - @ArtPJ”; the [Iranianflaghistory page](https://t.me/addemoji/Iranianflaghistory) identifies “IRAN Flag”. Both remain discovery-only until official pack import and semantic review.
- The inherited 178 `iranNewz` IDs retain their public-index provenance. The exact source post was not retained, and its direct pack page could not be rechecked in this audit. These IDs remain non-selectable; no fallback, label or political/cultural artwork is guessed.
- Ordinary sticker packs remain separate from custom emoji IDs.

## Validation and limits

Run:

```bash
python3 scripts/validate_skill.py
python3 scripts/validate_emoji_catalog.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

Behavioral tests cover import idempotence and metadata retention, authoritative fallback replacement, missing-response demotion, the 200-ID batch boundary, unexpected response IDs, Persian/ID search, blocked pending output, successful regional enrichment, unresolved sources, stale CSV detection, duplicate input and token-safe errors. CI runs them alongside the existing validation jobs.

The official Bot API 10.3 documentation was checked for message/custom-emoji fields, ordinary and rich buttons, and the enrichment batch limit. No bot token was supplied or read from deployment infrastructure; no Telegram metadata calls, delivery canaries, or visual previews were performed. `--verified-only` therefore currently returns no results. This is intentional and does not mean the source-mapped catalog is empty.

Next operational check: run official enrichment with a securely provided token, regenerate the CSV and validate. Preview selected assets and canary the intended bot/chat before making production appearance or eligibility claims. If revalidation disables a curated entry or template ID, validation fails until its references are reviewed; do not silently substitute another ID.
