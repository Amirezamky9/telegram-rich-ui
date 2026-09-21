# Ephemeral messages

## Table of contents

- [Purpose](#purpose)
- [Parameters](#parameters)
- [Sending](#sending)
- [Eligibility and delivery window](#eligibility-and-delivery-window)
- [Replacing callback messages](#replacing-callback-messages)
- [Editing and deleting](#editing-and-deleting)
- [Rich buttons and restrictions](#rich-buttons-and-restrictions)
- [Security model](#security-model)
- [Design guidance](#design-guidance)

## Purpose

Telegram Bot API 10.3 exposes `EphemeralMessageParameters` for messages that are visible to a specific receiving user in the supported group-style interaction context.

Use ephemeral delivery for user-specific responses that should not become ordinary shared chat content.

Do not confuse ephemeral messages with draft previews. Drafts are temporary generation previews in private chats; ephemeral messages are a separate message feature with their own parameters and edit/delete methods.

## Parameters

`EphemeralMessageParameters` contains:

- `receiver_user_id` - required target user;
- `callback_query_id` - optional callback query that the ephemeral message responds to;
- `replace_callback_query_message` - optional flag to replace the message that contained the pressed button when the API context permits it.

Use framework-native generated types rather than duplicating the schema by hand when possible.

## Sending

`sendRichMessage` accepts `ephemeral_message_parameters`.

Conceptual payload:

```json
{
  "chat_id": -1001234567890,
  "ephemeral_message_parameters": {
    "receiver_user_id": 123456789,
    "callback_query_id": "QUERY_ID"
  },
  "rich_message": {
    "html": "<p>Private result for this user.</p>"
  }
}
```

Do not assume every message method or every chat type accepts ephemeral parameters. Follow the current Bot API signature for the method you use.

## Eligibility and delivery window

Telegram documents ephemeral interactions for **groups and supergroups**. Delivery is best-effort and is not guaranteed, especially when the receiving user is offline.

For a non-admin bot, an ephemeral response to an eligible user action must be sent within the documented 15-second window and must be tied to the triggering interaction through either the relevant `callback_query_id` or an ephemeral reply target. If the bot is a chat administrator, Telegram allows it to send an ephemeral message to a non-bot member without that triggering identifier.

Treat these as API eligibility rules, not as authorization. Still verify that the requesting user is allowed to access the underlying data.

## Replacing callback messages

`replace_callback_query_message` was added in Bot API 10.3. Use it only when responding to the relevant callback flow and when replacement is the intended UX.

Keep callback authorization checks even though the output is user-specific.

## Editing and deleting

Telegram exposes dedicated ephemeral-message methods, including edit/delete variants. At Bot API 10.3, rich content can be supplied to the relevant ephemeral text edit method through its documented `rich_message` parameter.

Do not route an ephemeral message ID through ordinary message-edit assumptions without checking the method contract.

## Rich buttons and restrictions

Telegram documents that rich `login_url` buttons are not supported in ephemeral messages.

When building ephemeral rich UI:

- prefer callback/copy/other documented compatible actions;
- validate action restrictions before send;
- keep sensitive data out of button payloads even if the message itself is user-specific.

## Security model

Ephemeral visibility is not a replacement for authorization.

Before sending private user-specific data:

1. authenticate the callback/user identity using update data your bot can trust;
2. authorize access to the requested resource;
3. bind the ephemeral receiver to that user;
4. keep privileged data out of callback payloads and logs;
5. handle stale callback IDs gracefully.

Never infer authorization solely from the fact that an ephemeral message can be delivered.

## Design guidance

Good uses:

- per-user validation feedback in shared workflows;
- user-specific lookup results triggered from a shared message;
- private action confirmation without posting a normal shared message.

Avoid ephemeral delivery when:

- the information should be durable/history-visible;
- other participants need to see the result;
- the exact method/chat combination is not documented as supporting ephemeral parameters.

Do not bake exact human-readable error strings into application logic. Use the API status/code and documented fields.
