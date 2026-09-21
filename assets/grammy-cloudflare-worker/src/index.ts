import { Bot, webhookCallback } from "grammy";

interface Env {
  BOT_TOKEN: string;
  BOT_INFO: string;
  WEBHOOK_SECRET: string;
  MINI_APP_URL?: string;
}

function escapeHtml(value: unknown): string {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function makeHomeCard(name: string, miniAppUrl?: string) {
  const safeName = escapeHtml(name);
  const appButton = miniAppUrl?.startsWith("https://")
    ? `<tg-button type="web_app" style="success" url="${escapeHtml(miniAppUrl)}">Open Mini App</tg-button>`
    : `<tg-button type="callback_data" style="success" data="demo:help">Help</tg-button>`;

  return {
    html:
      `<h2>Welcome, ${safeName}</h2>` +
      `<p>This UI is rendered with Telegram rich messages.</p>` +
      `<table bordered striped compact>` +
      `<tr><th>Feature</th><th>Status</th></tr>` +
      `<tr><td>Rich UI</td><td><b>Ready</b></td></tr>` +
      `<tr><td>Cloudflare Worker</td><td><b>Ready</b></td></tr>` +
      `</table>` +
      `<tg-button-row align="center">` +
      `<tg-button type="callback_data" style="primary" data="demo:refresh">Refresh</tg-button>` +
      appButton +
      `</tg-button-row>`,
  };
}

function createBot(env: Env): Bot {
  const botInfo = JSON.parse(env.BOT_INFO);
  const bot = new Bot(env.BOT_TOKEN, { botInfo });

  bot.command("start", async (ctx) => {
    const name = ctx.from?.first_name ?? "there";
    await ctx.api.sendRichMessage(
      ctx.chat.id,
      makeHomeCard(name, env.MINI_APP_URL),
    );
  });

  bot.command("stream", async (ctx) => {
    if (ctx.chat.type !== "private") {
      await ctx.reply("Draft streaming is demonstrated only in a private chat.");
      return;
    }
    const draftId = (Date.now() % 2_000_000_000) || 1;
    await ctx.api.sendRichMessageDraft(
      ctx.chat.id,
      draftId,
      { html: "<tg-thinking>Preparing a rich result...</tg-thinking>" },
    );
    await ctx.api.sendRichMessage(ctx.chat.id, {
      html: "<p><b>Done.</b> This is the persistent final message.</p>",
    });
  });

  bot.callbackQuery("demo:refresh", async (ctx) => {
    await ctx.answerCallbackQuery({ text: "Refreshed" });
    const chatId = ctx.chat?.id;
    if (chatId === undefined) return;
    await ctx.api.sendRichMessage(chatId, {
      html: "<p>Callback handled successfully.</p>",
    });
  });

  bot.callbackQuery("demo:help", async (ctx) => {
    await ctx.answerCallbackQuery();
    const chatId = ctx.chat?.id;
    if (chatId === undefined) return;
    await ctx.api.sendRichMessage(chatId, {
      html: "<p>Configure MINI_APP_URL to add a private-chat Mini App button.</p>",
    });
  });

  return bot;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname !== "/telegram") {
      return new Response("Not found", { status: 404 });
    }
    if (request.method !== "POST") {
      return new Response("Method not allowed", { status: 405 });
    }
    const bot = createBot(env);
    return webhookCallback(bot, "cloudflare-mod", {
      secretToken: env.WEBHOOK_SECRET,
    })(request);
  },
};
