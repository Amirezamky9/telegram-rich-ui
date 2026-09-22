# aiogram 3.31+ Python recipes

## Table of contents

- [Supported baseline](#supported-baseline)
- [Install](#install)
- [Send rich HTML](#send-rich-html)
- [Send a typed JSON block tree](#send-a-typed-json-block-tree)
- [Edit rich content](#edit-rich-content)
- [Edit media in place](#edit-media-in-place)
- [Stream a rich draft](#stream-a-rich-draft)
- [Handle stop generation](#handle-stop-generation)
- [Ephemeral rich message](#ephemeral-rich-message)
- [Safe HTML composition](#safe-html-composition)
- [Rate-limit handling](#rate-limit-handling)
- [Fallback policy](#fallback-policy)
- [Version notes](#version-notes)

## Supported baseline

This repository was reviewed against **aiogram 3.31.0**.

aiogram 3.31.0 natively includes:

- `SendRichMessage`
- `SendRichMessageDraft`
- `InputRichMessage`
- generated rich block/input types
- `MessageGenerationStopped`
- current Bot API 10.3 parameters

Do not define a custom `TelegramMethod` for these methods on this baseline.

Avoid pinning aiogram 3.29.0. The aiogram changelog records a severe exponential slowdown for nested rich-block validation in that release; it was fixed in 3.29.1.

## Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install "aiogram==3.31.0"
```

For a maintained application, update the pin deliberately after reviewing aiogram's changelog and Telegram Bot API changes.

## Send rich HTML

```python
from aiogram import Bot
from aiogram.types import InputRichMessage

async def send_card(bot: Bot, chat_id: int) -> None:
    rich = InputRichMessage(
        html=(
            "<h3>Order</h3>"
            "<p>Your order is ready.</p>"
            "<tg-button-row align=\"center\">"
            "<tg-button type=\"callback_data\" style=\"primary\" "
            "data=\"order:details\">Details</tg-button>"
            "</tg-button-row>"
        )
    )
    await bot.send_rich_message(chat_id=chat_id, rich_message=rich)
```

For a handler responding to an incoming `Message`, aiogram also exposes rich-message shortcuts such as `answer_rich`/`reply_rich` in the reviewed release. Use the explicit bot method when a recipe must remain obvious to readers.

## Send a typed JSON block tree

Prefer aiogram's generated models when your application builds structured blocks. They protect you from stale field names.

Illustrative table imports (check current generated signatures in your installed release):

```python
from aiogram.types import InputRichMessage, InputRichBlockTable, RichBlockTableCell

rich = InputRichMessage(
    blocks=[
        InputRichBlockTable(
            type="table",
            cells=[
                [
                    RichBlockTableCell(text="Item", is_header=True),
                    RichBlockTableCell(text="Qty", is_header=True, align="right"),
                ],
                [
                    RichBlockTableCell(text="Keyboard"),
                    RichBlockTableCell(text="1", align="right"),
                ],
            ],
            is_bordered=True,
            is_compact=True,
        )
    ]
)
```

Because generated `RichText` typing can evolve, let your IDE/type checker guide the exact cell `text` representation in the installed aiogram release. The Telegram table container field is `cells`, never `rows`.

## Edit rich content

Use Telegram's existing `editMessageText` method through aiogram's native `edit_message_text` API with the current `rich_message` parameter.

```python
from aiogram.types import InputRichMessage

await bot.edit_message_text(
    chat_id=chat_id,
    message_id=message_id,
    rich_message=InputRichMessage(html="<p><b>Updated</b></p>"),
)
```

Do not create or call `editRichMessageText` as though it were a Telegram endpoint.

## Edit media in place

For a photo/video/card UI screen, keep the original message and edit it instead of deleting and resending it.

```python
from aiogram.types import InputMediaPhoto

await bot.edit_message_media(
    chat_id=chat_id,
    message_id=message_id,
    media=InputMediaPhoto(
        media=new_photo_file_id,
        caption="Updated product card",
    ),
    reply_markup=updated_keyboard,
)
```

aiogram also exposes `Message.edit_media(...)` as a context-aware shortcut. The same Bot API method can replace a text or rich message with media.

Route narrower edits to narrower methods:

```python
await bot.edit_message_caption(
    chat_id=chat_id,
    message_id=message_id,
    caption="Updated caption only",
)

await bot.edit_message_reply_markup(
    chat_id=chat_id,
    message_id=message_id,
    reply_markup=updated_keyboard,
)
```

For inline messages, do not pass a newly uploaded file to `edit_message_media`; use a prior `file_id` or URL. Respect album-type restrictions and the documented business-message edit window. Fall back to delete/send only when the requested transition is not supported or the target is no longer editable.

## Stream a rich draft

```python
from aiogram.types import InputRichMessage

async def stream_phase(bot: Bot, chat_id: int, draft_id: int) -> None:
    await bot.send_rich_message_draft(
        chat_id=chat_id,
        draft_id=draft_id,
        rich_message=InputRichMessage(
            html="<tg-thinking>Analyzing...</tg-thinking>"
        ),
        can_stop=True,
        keep_on_stop=True,
    )

    # ...perform/cancelable work...

    await bot.send_rich_message(
        chat_id=chat_id,
        rich_message=InputRichMessage(html="<p>Analysis complete.</p>"),
    )
```

The draft method targets private chats and returns a Boolean. The final method returns the persistent message.

## Handle stop generation

The exact Router filter expression can change with aiogram ergonomics, so bind to the typed update field exposed by your installed release instead of parsing raw JSON strings in application logic.

Architecture:

```python
active_tasks: dict[tuple[int, int], asyncio.Task] = {}

async def handle_generation_stopped(chat_id: int, draft_id: int) -> None:
    task = active_tasks.pop((chat_id, draft_id), None)
    if task is not None and not task.done():
        task.cancel()
```

Your update handler should extract `chat.id` and `draft_id` from aiogram's `MessageGenerationStopped` object and call this function.

Cancellation must be idempotent.

## Ephemeral rich message

Use aiogram's generated `EphemeralMessageParameters`:

```python
from aiogram.types import EphemeralMessageParameters, InputRichMessage

await bot.send_rich_message(
    chat_id=group_chat_id,
    rich_message=InputRichMessage(html="<p>Private result.</p>"),
    ephemeral_message_parameters=EphemeralMessageParameters(
        receiver_user_id=user_id,
        callback_query_id=callback_query_id,
    ),
)
```

Use only where the Telegram method/chat contract supports ephemeral delivery. Do not place `login_url` rich buttons in an ephemeral message.

## Safe HTML composition

Escape untrusted dynamic values:

```python
from html import escape


def text(value: object) -> str:
    return escape(str(value), quote=False)


def attr(value: object) -> str:
    return escape(str(value), quote=True)
```

Then:

```python
html = f"<p>Hello, <b>{text(user_name)}</b></p>"
```

Validate URL scheme/host separately; HTML escaping is not URL authorization.

Prefer rendering from a structured application model rather than concatenating dozens of arbitrary fragments.

## Rate-limit handling

aiogram 3.31.0 exposes `aiogram.exceptions.TelegramRetryAfter`; its `retry_after` attribute carries the retry delay supplied by Telegram. Catch it at the boundary where you can safely retry/coalesce the operation rather than sleeping blindly inside every handler.

Do not hard-code a belief that draft updates every 300 ms can never be throttled.

Recommended stream scheduler:

- coalesce tiny token deltas;
- send meaningful phase/content updates;
- cap in-flight updates to one per draft;
- back off on rate-limit responses;
- let finalization proceed even if an intermediate preview update was skipped.

## Fallback policy

Do not use:

```python
rich_html.replace("<table", "<pre").replace("</table>", "</pre>")
```

That leaves table rows/cells and other unsupported rich tags behind.

Instead:

- generate plain/legacy output from your structured data model; or
- use `scripts/legacy_fallback.py` for a safe plain-text conversion.

Only trigger a fallback intentionally. An arbitrary `TelegramBadRequest` can indicate a real programming defect that should be fixed.

## Version notes

When upgrading aiogram:

1. read its changelog;
2. verify the supported Telegram Bot API version;
3. run the repository validator;
4. type-check application code;
5. run a Telegram canary.

If the installed aiogram version predates native rich messages, prefer upgrading. Keep any raw/custom method compatibility shim isolated and explicitly version-gated rather than making it the normal path.
