# grammY TypeScript Recipes for Cloudflare Workers (Bot API 10.3)

This guide adapts the production patterns from `public/worker.js` into idiomatic TypeScript using the `grammY` framework on Cloudflare Workers. It details edge deployment, secret verification, typed raw Bot API 10.3 calls, safe HTML builders, channel administrative authorization, and Workers-specific runtime constraints.

---

## Deployment Architecture & Wrangler Configuration

Cloudflare Workers run on V8 isolates rather than a Node.js runtime. This environment provides sub-millisecond cold starts, global edge termination, and built-in Web standard APIs (`fetch`, `crypto.subtle`, `Response`, `Request`).

### `wrangler.jsonc` Setup
```jsonc
{
  "$schema": "node_modules/wrangler/config-schema.json",
  "name": "telerich-bot",
  "main": "src/index.ts",
  "compatibility_date": "2026-09-01",
  "compatibility_flags": ["nodejs_compat"],
  "vars": {
    "ALLOWED_ORIGIN": "https://studio.example.com"
  }
}
```

### Secrets Management
Configure runtime secrets via Wrangler CLI or the Cloudflare dashboard:
```bash
# Required bot token from @BotFather
npx wrangler secret put BOT_TOKEN

# Random secret string for webhook header verification
npx wrangler secret put WEBHOOK_SECRET

# Trusted operator authentication key for external browser administration
npx wrangler secret put ADMIN_KEY

# Optional comma-separated list of allowed admin numeric user IDs
npx wrangler secret put ADMINS_ID
```

### Environment Bindings Interface
```typescript
export interface Env {
  BOT_TOKEN: string;
  WEBHOOK_SECRET: string;
  ADMIN_KEY?: string;
  ADMINS_ID?: string;
  ALLOWED_ORIGIN?: string;
}
```

---

## Webhook Verification & Timing-Safe Comparison

Telegram delivers webhooks with the `X-Telegram-Bot-Api-Secret-Token` header. Always verify this secret using constant-time comparison via Web Crypto to prevent timing attacks.

```typescript
const encoder = new TextEncoder();

export async function constantTimeEqual(a: string, b: string): Promise<boolean> {
  const hash = async (s: string) =>
    new Uint8Array(await crypto.subtle.digest("SHA-256", encoder.encode(s)));
  const [ha, hb] = await Promise.all([hash(a), hash(b)]);
  if (ha.length !== hb.length) return false;
  let diff = 0;
  for (let i = 0; i < ha.length; i++) diff |= ha[i] ^ hb[i];
  return diff === 0;
}
```

---

## Typed Bot API 10.3 Raw Client

> **Assumption Notice:** As of standard releases of `@grammyjs/types`, Bot API 10.3 methods (`sendRichMessage`, `editRichMessageText`, `sendRichMessageDraft`) are not fully typed in the core library. Use grammY's `bot.api.raw` interface combined with explicit TypeScript contracts:

```typescript
import { Bot, Context } from "grammy";
import { Message, InlineKeyboardMarkup } from "grammy/types";

export interface InputRichMessage {
  html?: string;
  markdown?: string;
  blocks?: any[];
  is_rtl?: boolean;
}

export interface SendRichMessagePayload {
  chat_id: number | string;
  rich_message: InputRichMessage;
  message_thread_id?: number;
  disable_notification?: boolean;
  protect_content?: boolean;
  ephemeral_message_parameters?: {
    receiver_user_id?: number;
    callback_query_id?: string;
  };
  reply_markup?: InlineKeyboardMarkup;
}

export interface EditRichMessagePayload {
  chat_id?: number | string;
  message_id?: number;
  inline_message_id?: string;
  rich_message: InputRichMessage;
  reply_markup?: InlineKeyboardMarkup;
}

// Type-safe raw execution wrappers
export async function sendRichMessage(
  bot: Bot<Context>,
  payload: SendRichMessagePayload
): Promise<Message> {
  return await bot.api.raw.sendRichMessage(payload as any) as Message;
}

export async function editRichMessageText(
  bot: Bot<Context>,
  payload: EditRichMessagePayload
): Promise<Message> {
  return await bot.api.raw.editMessageText(payload as any) as Message;
}
```

### فارسی — معماری ورکر و کلودفلر
- محیط Cloudflare Workers از ایزوله‌های V8 استفاده می‌کند و سبک‌تر و سریع‌تر از سرورهای معمولی Node.js است.
- اعتبارسنجی توکن وب‌هوک با تابع `constantTimeEqual` و Web Crypto انجام می‌شود تا در برابر حملات تحلیل زمانی (Timing Attacks) ایمن باشد.
- از آنجا که پکیج رسمی `@grammyjs/types` ممکن است هنوز متدهای جدید نسخه ۱۰.۳ تلگرام را تایپ نکرده باشد، با استفاده از `bot.api.raw` و تایپ‌های سفارشی، ارسال پیام ریچ بدون ارور کامپایل تایپ‌اسکریپت پیاده‌سازی می‌شود.

---

## Type-Safe HTML Builders

```typescript
export function escapeHtml(value: unknown): string {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

export interface TableOptions {
  bordered?: boolean;
  striped?: boolean;
  compact?: boolean;
  caption?: string;
}

export function buildRichTable(
  headers: string[],
  rows: (string | number)[][],
  options: TableOptions = {}
): string {
  const flags = [
    options.bordered !== false ? "bordered" : "",
    options.striped !== false ? "striped" : "",
    options.compact !== false ? "compact" : "",
  ].filter(Boolean).join(" ");

  const headerCells = headers
    .map((h) => `    <th>${escapeHtml(h)}</th>`)
    .join("\n");

  const bodyRows = rows
    .map((row) =>
      "  <tr>\n" +
      row.map((cell) => `    <td>${escapeHtml(cell)}</td>`).join("\n") +
      "\n  </tr>"
    )
    .join("\n");

  const captionTag = options.caption
    ? `  <caption>${escapeHtml(options.caption)}</caption>\n`
    : "";

  return `<table ${flags}>\n${captionTag}  <tr>\n${headerCells}\n  </tr>\n${bodyRows}\n</table>`;
}

export interface RichButton {
  type: "url" | "callback_data" | "web_app" | "copy_text" | "disabled" | "switch_inline_query";
  label: string;
  style?: "primary" | "success" | "danger" | "link";
  url?: string;
  data?: string;
  text?: string;
  query?: string;
}

export function buildRichButtonRow(
  buttons: RichButton[],
  align: "left" | "center" | "right" = "left"
): string {
  const rendered = buttons.map((b) => {
    const attrs = [`type="${b.type}"`];
    if (b.style) attrs.push(`style="${b.style}"`);
    if (b.url) attrs.push(`url="${escapeHtml(b.url)}"`);
    if (b.data) attrs.push(`data="${escapeHtml(b.data)}"`);
    if (b.text) attrs.push(`text="${escapeHtml(b.text)}"`);
    if (b.query) attrs.push(`query="${escapeHtml(b.query)}"`);
    return `  <tg-button ${attrs.join(" ")}>${escapeHtml(b.label)}</tg-button>`;
  });

  return `<tg-button-row align="${align}">\n${rendered.join("\n")}\n</tg-button-row>`;
}
```

---

## Complete Worker Handler & Webhook Integration

```typescript
import { Bot, webhookCallback } from "grammy";

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    // 1. Webhook endpoint
    if (url.pathname === "/webhook") {
      if (request.method !== "POST") {
        return new Response("Method Not Allowed", { status: 405 });
      }

      // Timing-safe secret token verification
      const secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token") || "";
      if (!env.WEBHOOK_SECRET || !(await constantTimeEqual(secret, env.WEBHOOK_SECRET))) {
        return new Response("Unauthorized", { status: 401 });
      }

      // Initialize bot per-request inside Workers
      const bot = new Bot(env.BOT_TOKEN);

      // Register handlers
      bot.command("catalog", async (ctx) => {
        const table = buildRichTable(
          ["Service", "Tier", "Monthly"],
          [
            ["Redis Cache", "Standard", "$15"],
            ["Workers KV", "Unlimited", "$5"],
          ],
          { caption: "Cloud Infrastructure" }
        );
        const buttons = buildRichButtonRow(
          [
            { type: "callback_data", style: "success", label: "Subscribe", data: "plan:sub:redis" },
            { type: "copy_text", label: "Coupon", text: "EDGE2026" },
          ],
          "center"
        );

        await sendRichMessage(bot, {
          chat_id: ctx.chat.id,
          rich_message: { html: `<h3>Edge Products</h3>\n${table}\n${buttons}` },
        });
      });

      bot.on("callback_query:data", async (ctx) => {
        await ctx.answerCallbackQuery({ text: "Processing your selection..." });
        if (ctx.callbackQuery.data === "plan:sub:redis" && ctx.msg) {
          await editRichMessageText(bot, {
            chat_id: ctx.chat.id,
            message_id: ctx.msg.message_id,
            rich_message: {
              html: "<p>✅ <b>Subscribed to Redis Cache</b></p><p>Check your dashboard for credentials.</p>",
            },
          });
        }
      });

      // Delegate update parsing and handling to grammY
      return webhookCallback(bot, "cloudflare-update")(request);
    }

    return new Response("TeleRich Bot Worker Active", { status: 200 });
  },
};
```

---

## Channel Publishing & Administrative Pre-Checks

When publishing rich messages to channels or groups, `public/worker.js` enforces dual administrative checks (`getChatMember` for both user and bot) to prevent unauthorized posting:

```typescript
export async function authorizeChannelPublish(
  bot: Bot<Context>,
  chatId: number | string,
  userId: number
): Promise<boolean> {
  const [botMember, userMember] = await Promise.all([
    bot.api.getChatMember(chatId, bot.botInfo?.id || (await bot.api.getMe()).id),
    bot.api.getChatMember(chatId, userId),
  ]);

  // Both user and bot must be administrators or creators
  const validStatus = ["administrator", "creator"];
  if (!validStatus.includes(botMember.status) || !validStatus.includes(userMember.status)) {
    throw new Error("Both bot and user must be administrators of the destination channel.");
  }

  // The bot must have explicit permission to post messages in channels
  if (botMember.status === "administrator" && !("can_post_messages" in botMember && botMember.can_post_messages)) {
    throw new Error("Bot lacks 'can_post_messages' administrator permission in channel.");
  }

  return true;
}
```

---

## Cloudflare Workers Runtime Constraints

1. **No Node.js Built-in APIs:** Workers do not include `fs`, `net`, `child_process`, or Node's `crypto`. Always use `crypto.subtle` and Web APIs.
2. **Stateless Execution:** Do not store sessions in in-memory global variables. Use Telegram callback data, Cloudflare KV, or encrypted cookies.
3. **Execution Limits:** Free tier allows 50ms CPU time; Paid tier allows up to 30s. Use `ctx.waitUntil()` for asynchronous tasks like telemetry or logging that do not delay the HTTP response.
4. **Fire-and-Forget Pattern:** When Telegram webhooks arrive, acknowledge quickly (`200 OK`) and wrap long-running operations inside `ctx.waitUntil(promise)` to prevent Telegram webhook timeouts.

### فارسی — امنیت انتشار و محدودیت‌های محیط ورکر
- قبل از ارسال پیام به کانال‌ها، حتماً دسترسی ادمین بودن کاربر و ربات و مجوز `can_post_messages` بررسی می‌شود تا از ارسال بدون مجوز جلوگیری گردد.
- محیط ورکر حافظه پایدار ندارد (Stateless)؛ بنابراین اطلاعات حالت نباید در متغیرهای سراسری ذخیره شوند.
- با استفاده از `ctx.waitUntil` می‌توان کارهای پس‌زمینه را بدون معطل کردن پاسخ وب‌هوک انجام داد.

