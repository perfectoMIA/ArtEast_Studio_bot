import asyncio
from datetime import date, datetime
from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from models import DataBase
from config import ADMINS_ID
from keyboards import inline as inline_keyborads


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


async def back_to_tag_information(tag_name: str, message: Message, state: FSMContext):
    markup = inline_keyborads.get_tag_information_keyboard(tag_name)
    description = DataBase.Get_tag_description(tag_name)[0][0]
    list_users = DataBase.Get_users_from_tag(tag_name)
    users = ""
    for i in range(len(list_users)):
        users += "@" + " ".join(list(list_users[i]))
        users += "\n"
    await message.bot.edit_message_text(chat_id=message.chat.id, message_id=(await state.get_data())["message_id"],
                                        text=f"Название тега: {tag_name}\n"
                                             f"Описание тега: {str(description)}\n"
                                             f"Участники тега:\n{users}",
                                        reply_markup=markup)


def sort_birthday(user: tuple):
    return datetime.strptime(user[1], "%d.%m.%Y")
