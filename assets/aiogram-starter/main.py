from __future__ import annotations

import asyncio
import os
import time
from html import escape

from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, InputRichMessage, Message

router = Router()


def safe(value: object) -> str:
    return escape(str(value), quote=False)


def home_card(first_name: str) -> InputRichMessage:
    name = safe(first_name)
    return InputRichMessage(
        html=(
            f"<h2>Welcome, {name}</h2>"
            "<p>This bot uses Telegram Bot API rich messages.</p>"
            "<table bordered compact>"
            "<tr><th>Feature</th><th>Status</th></tr>"
            "<tr><td>Rich UI</td><td><b>Ready</b></td></tr>"
            "<tr><td>Draft streaming</td><td><b>Ready</b></td></tr>"
            "</table>"
            "<tg-button-row align=\"center\">"
            "<tg-button type=\"callback_data\" style=\"primary\" data=\"demo:refresh\">Refresh</tg-button>"
            "</tg-button-row>"
        )
    )


@router.message(CommandStart())
async def start(message: Message, bot: Bot) -> None:
    if message.from_user is None:
        return
    await bot.send_rich_message(
        chat_id=message.chat.id,
        rich_message=home_card(message.from_user.first_name),
    )


@router.message(Command("stream"))
async def stream(message: Message, bot: Bot) -> None:
    if message.chat.type != ChatType.PRIVATE:
        await message.answer("Draft streaming is demonstrated only in a private chat.")
        return
    draft_id = (int(time.time() * 1000) % 2_000_000_000) or 1
    await bot.send_rich_message_draft(
        chat_id=message.chat.id,
        draft_id=draft_id,
        rich_message=InputRichMessage(
            html="<tg-thinking>Preparing a rich result...</tg-thinking>"
        ),
    )
    await asyncio.sleep(0.5)
    await bot.send_rich_message(
        chat_id=message.chat.id,
        rich_message=InputRichMessage(
            html="<p><b>Done.</b> The final rich message is persistent.</p>"
        ),
    )


@router.callback_query(lambda q: q.data == "demo:refresh")
async def refresh_callback(query: CallbackQuery) -> None:
    await query.answer("Refreshed")
    if isinstance(query.message, Message):
        await query.message.answer("The callback was handled.")


async def main() -> None:
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError("Set BOT_TOKEN in the environment")
    bot = Bot(token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
