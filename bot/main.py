import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers import routers
from bot.config import BOT_TOKEN
from bot.passive_functions import birthday_notice, spam_mailing, delete_message, Spam_about_money


# Функция запуска бота
async def main():
    # включаем логирование
    logging.basicConfig(level=logging.INFO)
    # создаём экземпляры бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    # подключаем все роутеры к диспетчеру
    for router in routers:
        dp.include_router(router)
    # запускаем бота
    try:
        await asyncio.gather(
            bot.delete_webhook(drop_pending_updates=False),
            dp.start_polling(bot),
            birthday_notice(bot),  # отправка уведомлений о скором дне рождения
            spam_mailing(bot),  # отправка сообщеий о заполнении рабочих часов за день
            Spam_about_money(bot),
            return_exceptions=True
            #delete_message(bot)
        )
    finally:
        await bot.session.close()

# работает если мы запускаем этот код как главный.
if __name__ == "__main__":
    asyncio.run(main())
