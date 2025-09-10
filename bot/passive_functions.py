import asyncio
from datetime import date, datetime
from aiogram import Bot

from models import DataBase
from config import ADMINS_ID


# отравка сообщений админам о скором дне рождения
async def birthday_notice(bot: Bot):
    persons = DataBase.Get_users_with_birth_date()
    today = date.today()
    admins_id = str(ADMINS_ID).split(',')
    for person in persons:
        birthday = datetime.strptime(person[1], "%d.%m.%Y")
        if today.month == birthday.month and today.day + 7 == birthday.day:
            for ID in admins_id:
                await bot.send_message(chat_id=ID, text=f"через 7 дней день рождения у: @{person[0]}")
    await asyncio.sleep(86400)  # раз в сутки запускается
