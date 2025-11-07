import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message

from bot.config import BOT_TOKEN


with open("..\TEXT_SPAM_MONEY.txt", "r", encoding="utf-8") as file:
    text = file.readlines()
print(text)
answer = ""
for s in text:
    answer += s


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def func():
    await bot.send_message(text=answer, chat_id=2081599417, parse_mode="Markdown")


@dp.message()
async def func2(mess: Message):
    await bot.copy_message(chat_id=2081599417, from_chat_id=2081599417, message_id=mess.message_id)
    with open("telegram message/test text.md", "w", encoding='utf-8') as file:
        file.write(mess.text)


asyncio.run(dp.start_polling(bot))
