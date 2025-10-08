import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import routers
from config import BOT_TOKEN
from passive_functions import birthday_notice, spam_mailing


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
            bot.delete_webhook(drop_pending_updates=True),
            dp.start_polling(bot),
            birthday_notice(bot),  # отправка уведомлений о скором дне рождения
            spam_mailing(bot)  # отправка сообщеий о заполнении рабочих часов за день
        )
    finally:
        await bot.session.close()

# работает если мы запускаем этот код как главный.
if __name__ == "__main__":
    asyncio.run(main())
