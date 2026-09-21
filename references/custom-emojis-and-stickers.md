# Premium custom emoji and sticker usage

## Table of contents

- [Agent policy](#agent-policy)
- [Official Telegram rules](#official-telegram-rules)
- [Local registry](#local-registry)
- [Searching the registry](#searching-the-registry)
- [Using emoji in rich text](#using-emoji-in-rich-text)
- [Using emoji on buttons](#using-emoji-on-buttons)
- [Persian and Iranian coverage](#persian-and-iranian-coverage)
- [Importing and enriching packs](#importing-and-enriching-packs)
- [Deduplication](#deduplication)
- [AIActions](#aiactions)
- [Verification](#verification)

## Agent policy

For polished bot UI, prefer a suitable **premium custom emoji** from the local registry for major
semantic cues such as status, navigation, payments, shop actions, support, AI/thinking, warnings,
and section headers. Do not fall back to plain Unicode merely because it is easier when a good
registry match exists.

However, do not decorate every line. Prefer one coherent visual family per card/screen and keep
important meaning understandable from text.

Never use a registry record with `selectable: false`.

## Official Telegram rules

Telegram requires a valid alternative emoji for custom emoji entities. The alternative is shown
where the custom emoji cannot be displayed; Telegram recommends using the emoji from the custom
emoji sticker's `emoji` field.

At the reviewed Bot API version, bots can use custom emoji in messages they directly send to
private, group, and supergroup chats when the human owner of the bot has Telegram Premium. Bots
with qualifying additional usernames purchased on Fragment have another eligibility path.

`getMe` does not reveal the owner's Premium state.

## Local registry

For the full registry contract, curated sets, CSV workflow, button recipes, and Persian/Iranian import policy, read `references/premium-emoji-registry.md`.

Read:

- `assets/emoji-catalog/curated-ui.json` first for UI work.
- `assets/emoji-catalog/catalog.json` for broad search.
- `assets/emoji-catalog/regional-packs.json` for Persian/Iranian pack inventory.

The registry is deduplicated by `custom_emoji_id`. Read `references/curated-emoji-guide.md` for the 47 annotated UI choices and `references/emoji-registry-audit.md` for verification limits.

A ready record contains at least:

- `custom_emoji_id`
- `fallback`
- semantic key/aliases
- category/style metadata
- provenance
- `selectable: true`

## Searching the registry

Examples:

```bash
python3 scripts/search_emoji.py settings
python3 scripts/search_emoji.py پرداخت --limit 8
python3 scripts/search_emoji.py iran --tag persian_ui
python3 scripts/search_emoji.py ai --format html
```

Agents should prefer `curated-ui.json` when it contains a semantic match, because its entries have reviewed semantic guidance. Check each set’s `style_policy`: some mix
source families, and none has a visual-review guarantee.

## Using emoji in rich text

Rich HTML:

```html
<tg-emoji emoji-id="5877260593903177342">⚙️</tg-emoji> Settings
```

Rich Markdown:

```markdown
![Image: ⚙️](tg://emoji?id=5877260593903177342) Settings
```

The fallback must match the registry record.

## Using emoji on buttons

Telegram Bot API 9.4+ supports `icon_custom_emoji_id` on ordinary
`InlineKeyboardButton` and `KeyboardButton`. This is ideal when an action should have a premium
icon without embedding a raw emoji character in the button label.

For **RichMessageButton**, the button's rich text may contain `RichTextCustomEmoji`, so a
`<tg-emoji>` can be part of the rich button text when using rich-message HTML.

Example ordinary inline keyboard (conceptual JSON):

```json
{
  "text": "Settings",
  "icon_custom_emoji_id": "5877260593903177342",
  "callback_data": "settings"
}
```

Keep the same eligibility rules as custom emoji in messages.

## Persian and Iranian coverage

The registry includes two layers:

1. ready cultural entries with source-mapped fallbacks, including the Iran flag and useful Nowruz/Yalda
   visual vocabulary;
2. raw IDs from the public `iranNewz` custom-emoji pack plus discovered packs such as
   `Emojiran` and `Iranianflaghistory`.

Raw regional IDs are deliberately **non-selectable** until enriched with Telegram Bot API metadata.
This prevents an agent from inventing a fallback emoji.

Regular `t.me/addstickers/...` sticker packs are not mixed into this custom-emoji registry.

## Importing and enriching packs

Import a known custom emoji pack:

```bash
BOT_TOKEN=... python3 scripts/import_emoji_pack.py iranNewz --write
```

Enrich raw IDs already stored in the catalog:

```bash
BOT_TOKEN=... python3 scripts/enrich_custom_emoji.py --write
```

Both scripts use official Bot API metadata and merge by ID, so they do not create duplicates.

## Deduplication

The registry invariant is:

```text
one custom_emoji_id -> one catalog record
```

If the same ID appears under several names/packs/sources, merge those values into aliases, packs,
keywords, tags, and provenance.

Run:

```bash
python3 scripts/validate_emoji_catalog.py
```

before committing registry changes.

## AIActions

Telegram's rich-message documentation points to the AIActions custom emoji pack for examples used
inside draft-only `<tg-thinking>`.

Use AIActions for AI generation/thinking states where appropriate, but do not make the streaming
protocol depend on one visual pack.

## Verification

For production-critical use:

1. search/select a ready registry entry;
2. send a canary in the actual target chat type;
3. confirm the bot is eligible to use custom emoji there;
4. keep the fallback meaningful;
5. if a stored ID stops working, enrich/verify against Telegram instead of inventing a replacement.
