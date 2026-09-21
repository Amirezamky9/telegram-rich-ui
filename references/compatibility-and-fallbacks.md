# Compatibility and fallbacks

## Table of contents

- [Principle](#principle)
- [Do not guess client fallback](#do-not-guess-client-fallback)
- [Native-first framework policy](#native-first-framework-policy)
- [Fallback classes](#fallback-classes)
- [Safe plain-text fallback](#safe-plain-text-fallback)
- [Error classification](#error-classification)
- [Version gates](#version-gates)
- [Canary strategy](#canary-strategy)

## Principle

Compatibility is an application responsibility. Do not convert undocumented client behavior into a Telegram server contract.

A reliable bot has two explicit rendering paths when necessary:

1. rich path;
2. deliberately generated legacy/plain path.

## Do not guess client fallback

This repository intentionally does not promise that old clients will:

- transform tables into a particular text format;
- move rich buttons into keyboard rows;
- show the first slideshow item;
- preserve every caption/layout detail.

Those behaviors can vary by client version and are not a stable API contract unless Telegram documents them.

If legacy behavior matters, generate a fallback yourself and test it.

## Native-first framework policy

Reviewed baseline:

- aiogram 3.31.0 has native `SendRichMessage`, `SendRichMessageDraft`, `InputRichMessage`, and rich block types.
- grammY 1.46.0 has native `sendRichMessage`, `sendRichMessageDraft`, `sendMessageDraft`, and current Telegram types.

Therefore:

- do not define a custom aiogram `TelegramMethod` for current rich-message methods unless supporting an older explicitly pinned aiogram version;
- do not cast grammY's normal rich-message calls to `any` in current code;
- prefer an upgrade over maintaining a permanent raw-method shim.

## Fallback classes

### Intentional compatibility fallback

Use when your product explicitly supports an environment where rich UI is unavailable or undesirable.

Example: render a table as plain aligned/list text and send via `sendMessage`.

### Capability fallback

Use after a narrowly identified capability check/failure, not after any `400 Bad Request`.

### Transport retry

Network errors and rate limits are not format fallbacks. Retry/back off according to the failure type.

### Programming defect

Invalid markup, invalid table shape, unsupported action combination, or wrong method name is a defect. Surface/fix it instead of silently sending a simpler message.

## Safe plain-text fallback

Use `scripts/legacy_fallback.py` to turn rich HTML into readable plain text. It parses markup and emits text/block boundaries; it does not perform fragile string substitutions like replacing only `<table>` with `<pre>` while leaving invalid `<tr>`/`<td>` tags behind.

Example:

```bash
python3 scripts/legacy_fallback.py assets/templates/invoice-receipt.html
```

For production data, consider generating both rich and fallback outputs from the same structured application model rather than converting one into the other.

## Error classification

Recommended decision tree:

```text
API call failed
  |-- 429 / retry information -> rate-limit handling
  |-- network timeout/reset -> bounded transport retry
  |-- known capability/version mismatch -> explicit fallback path
  |-- invalid parameters/markup/schema -> programming/content defect
  `-- permission/auth -> fix permissions/credentials; do not format-fallback
```

Do not branch on exact English `description` text. Telegram describes it as human-readable, and Telegram also notes that numeric `error_code` contents may change. Prefer framework-typed exceptions plus documented response parameters such as retry information.

## Version gates

When you intentionally support older frameworks:

- document the exact supported versions;
- run a feature check at startup/build time;
- keep compatibility code isolated;
- delete it when the support window closes.

Do not leave "maybe the framework does not support this" code in the main path after the maintained framework already supports it.

## Canary strategy

A good canary verifies semantics, not just keyword visibility.

Minimum pre-release canary:

1. send a simple rich paragraph;
2. send a table generated from the canonical schema;
3. send a rich button row and exercise callback handling;
4. run a draft -> update -> final flow in a private chat;
5. test stop-generation handling if enabled;
6. send one RTL message;
7. if relevant, test custom emoji with a fallback;
8. run plain fallback intentionally;
9. inspect logs for hidden 400/429 errors.

Keyword checks can confirm agent sync, but they do not prove schema correctness.
