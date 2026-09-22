# Slideshow and media

## Table of contents

- [Media model](#media-model)
- [HTML and Markdown media blocks](#html-and-markdown-media-blocks)
- [Collage and slideshow](#collage-and-slideshow)
- [InputRichMessageMedia](#inputrichmessagemedia)
- [Editing existing messages in place](#editing-existing-messages-in-place)
- [Telegram media identifiers](#telegram-media-identifiers)
- [JSON media blocks](#json-media-blocks)
- [Draft restrictions](#draft-restrictions)
- [Caching strategy](#caching-strategy)
- [Security and reliability](#security-and-reliability)
- [Examples](#examples)

## Media model

Rich messages can contain media as separate blocks. Telegram documents photo, video, animation, audio, document, and voice-note rich blocks, plus collage and slideshow containers.

For Rich HTML/Markdown, media blocks support HTTP and HTTPS URLs. Media type is determined from MIME type and URL. If you need to send media explicitly rather than rely on URL fetching, use `InputRichMessage.media` and reference each item by a Telegram `tg://...` identifier.

Media blocks are separate blocks; do not embed arbitrary media inside table cells or other inline-only contexts.

## HTML and Markdown media blocks

Documented HTML examples include:

```html
<img src="https://example.com/photo.jpg"/>
<video src="https://example.com/video.mp4"></video>
<audio src="https://example.com/audio.mp3"></audio>
<tg-document src="https://example.com/manual.pdf"></tg-document>
```

Use the exact tag/attribute syntax documented by the current Telegram API. Do not add codec, file-size, timeout, or CDN guarantees to this skill unless Telegram documents them for rich messages.

## Collage and slideshow

### Collage

```html
<tg-collage>
  <img src="https://example.com/1.jpg"/>
  <img src="https://example.com/2.jpg"/>
  <figcaption>Gallery<cite>Example Store</cite></figcaption>
</tg-collage>
```

### Slideshow

```html
<tg-slideshow>
  <img src="https://example.com/1.jpg"/>
  <video src="https://example.com/demo.mp4"></video>
  <figcaption>Product tour<cite>Example Store</cite></figcaption>
</tg-slideshow>
```

In Rich Markdown, Telegram also permits Markdown media blocks inside `tg-collage` and `tg-slideshow`.

Do not promise a particular swipe animation, fallback album behavior, or legacy-client transformation as an API contract. Those are client behaviors and can vary.

## InputRichMessageMedia

`InputRichMessage.media` is a list of `InputRichMessageMedia` objects. Each object has:

- `id`: 1-64 characters; only ASCII letters, digits, `_`, and `-` are allowed;
- `media`: one of Telegram's supported input media types for rich messages.

Media-specific properties outside the media itself/properties are ignored according to the Bot API description.

Example conceptual payload:

```json
{
  "html": "<img src=\"tg://photo?id=hero\"/>",
  "media": [
    {
      "id": "hero",
      "media": {
        "type": "photo",
        "media": "AgAC..."
      }
    }
  ]
}
```

Use framework-native media classes for production code so the exact current type shape is checked by the framework.

## Editing existing messages in place

For card-like bot UI, retain the existing `message_id` and mutate the message whenever the Bot API exposes a matching edit method. Delete-and-resend is a fallback, not the normal navigation pattern.

| Desired UI change | Preferred API |
| --- | --- |
| Replace photo/video/animation/audio/document/live photo content | `editMessageMedia` |
| Replace a text or rich message with media | `editMessageMedia` |
| Change only a media caption | `editMessageCaption` |
| Change only an inline keyboard | `editMessageReplyMarkup` |
| Edit ephemeral media/caption/keyboard/text | matching `editEphemeralMessage*` method |
| Convert a conventional media message to text-only/rich-only | Do not assume support; use a deliberate replacement fallback if no documented edit path applies |

`editMessageMedia` accepts a new `InputMedia` object and a new inline keyboard. Put the new caption in the `InputMedia` object when media and caption change together, so one API call can represent the UI transition.

Operational rules:

- Do not delete and resend a product card, gallery card, order card, or menu screen solely because its photo/video changes.
- For ordinary non-inline messages, use Telegram-hosted `file_id` values when practical; framework-supported uploads remain available where the Bot API permits them.
- For inline messages, a new file cannot be uploaded during `editMessageMedia`; use an existing `file_id` or URL.
- For album members, preserve the documented category: audio albums stay audio, document albums stay document, and other media albums stay within photo/live-photo/video.
- Certain business messages not sent by the bot and without an inline keyboard can only be edited within 48 hours.
- If Telegram rejects the edit because the target is no longer editable or the requested type transition is unsupported, perform an explicit replacement flow and update any stored `message_id` atomically.

History note: Bot API 7.11 (2024-10-31) explicitly added text-to-media replacement via `editMessageMedia`. Current Bot API 10.3 also documents rich-message-to-media replacement.

## Telegram media identifiers

Telegram documents these rich-message references:

- `tg://photo?id=...`
- `tg://video?id=...`
- `tg://document?id=...`
- `tg://audio?id=...`

The identifier after `id=` refers to the matching `InputRichMessageMedia.id`, not to an arbitrary filesystem path.

Example:

```html
<tg-slideshow>
  <img src="tg://photo?id=front"/>
  <img src="tg://photo?id=back"/>
</tg-slideshow>
```

with `media` entries named `front` and `back`.

## JSON media blocks

When using `blocks`, use the documented `InputRichBlock*` media types rather than inventing a generic `src` field. Examples include:

- `photo`
- `video`
- `animation`
- `audio`
- `document`
- `voice_note`
- `collage`
- `slideshow`

Collage/slideshow `blocks` contain nested input rich blocks and may include a documented caption.

## Draft restrictions

`sendRichMessageDraft` does not support direct upload of new files or explicit upload of files by URL. For draft streaming:

- prefer text/thinking/structure that does not require a new upload;
- if media is already represented in a supported form, verify the exact current Bot API behavior before depending on it;
- persist the final message with `sendRichMessage`.

Do not build an AI streaming flow that repeatedly uploads media on every draft refresh.

## Caching strategy

Project recommendation:

1. Reuse Telegram-hosted file identifiers when your existing bot workflow already has them.
2. For rich HTML/Markdown composition, map application media keys to `InputRichMessageMedia.id` values.
3. Cache only identifiers your application can safely reuse.
4. Keep source URLs and Telegram file identifiers conceptually separate.

This is application architecture, not a Telegram requirement.

## Security and reliability

- Only allow expected URL schemes. For remote rich media, use HTTP/HTTPS as documented by Telegram; prefer HTTPS operationally.
- Do not fetch user-supplied URLs server-side without SSRF controls.
- Do not accept arbitrary local paths from user content.
- Limit media count before sending; Telegram's rich-message maximum is 50 attachments.
- Validate `InputRichMessageMedia.id` against `[A-Za-z0-9_-]{1,64}`.
- Avoid retrying failed uploads blindly; distinguish invalid media, permissions, transport failures, and rate limits.

## Examples

### Product slideshow with explicit media mapping

```json
{
  "html": "<tg-slideshow><img src=\"tg://photo?id=p1\"/><img src=\"tg://photo?id=p2\"/><figcaption>Two views</figcaption></tg-slideshow>",
  "media": [
    {"id": "p1", "media": {"type": "photo", "media": "FILE_ID_1"}},
    {"id": "p2", "media": {"type": "photo", "media": "FILE_ID_2"}}
  ]
}
```

### Public URL collage

```html
<tg-collage>
  <img src="https://cdn.example.com/a.jpg"/>
  <img src="https://cdn.example.com/b.jpg"/>
</tg-collage>
```

Use Telegram's current generated framework types when implementing the JSON media objects in aiogram or grammY.
