import asyncio
import time
from datetime import date, datetime, timedelta
from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.models import DataBase
from bot.keyboards import inline as inline_keyborads


# отравка сообщений админам о скором дне рождения
async def birthday_notice(bot: Bot):
    while True:
        persons = DataBase.Get_users_with_birth_date()
        i = 0
        while i < len(persons):  # удаляем всех пользователей без др
            if persons[i][1] == "None":
                persons.pop(i)
            else:
                i += 1
        today = date.today()
        admins_id = DataBase.Get_admins_id()
        for i in range(len(admins_id)):
            admins_id[i] = admins_id[i][0]
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


# отправка сообщений о заполнении часов работы
async def spam_mailing(bot: Bot):
    while True:
        now = datetime.now()
        if now.hour == 00:  # час в который бот будет рассылать сообщение
            users = DataBase.Get_users_to_spam()
            for i in range(len(users)):
                users[i] = users[i][0]

            count_column = DataBase.Get_count_column()
            today = date.today()
            if count_column > 5:
                # удаление дня, который уже проверен
                DataBase.Delete_column_by_name_in_Spam(str((today - timedelta(days=3)).strftime("%d.%m.%Y")))
            # добавление нового дня, для заполнения часов
            DataBase.Add_column_by_name_in_Spam(today.strftime("%d.%m.%Y"))
            yesterday = today - timedelta(days=1)
            markup = inline_keyborads.spam_mailing(yesterday.strftime("%d.%m.%Y"))

            for user_id in users:
                await bot.send_message(chat_id=user_id,
                                       text=f"Ты заполнил рабочие часы за {yesterday.strftime('%d.%m.%Y')}?",
                                       reply_markup=markup)
            await asyncio.sleep(86400)
        else:
            next_day = now + timedelta(days=1)
            next_day = next_day.replace(hour=00, microsecond=0, second=0, minute=0)
            await asyncio.sleep((next_day - now).seconds)
