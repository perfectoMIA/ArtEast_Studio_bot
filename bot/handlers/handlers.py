from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram import F
from datetime import datetime, date
import math
from aiogram.filters import Command

from bot.models import DataBase
import bot.keyboards.inline as inline_keyborads
from bot.passive_functions import sort_birthday
from bot.config import CHAT_ID

router = Router()


# новый пользователь в чате добавляется в бд.
# @router.message(lambda message: message.new_chat_members is not None)
# async def biba(message: Message):  # переименовать
#     DataBase.Add_user(message.new_chat_members[0].id, message.new_chat_members[0].username)  # не робит
#     spisok = DataBase.Get_users()
#     await message.answer(f"Список пользователей: {spisok}")


# покинувший чат пользователь удаляется из бд
# @router.message(lambda message: message.left_chat_member)
# async def boba(message: Message):  # переименовать
#     DataBase.Delete_user(message.left_chat_member.username)
#     spisok = DataBase.Get_users()
#     await message.answer(f"Список пользователей: {spisok}")


# показать все теги в виде кнопок
@router.callback_query(F.data.in_({"all_tags", "back_to_all_tags"}))
async def get_all_tags(call: CallbackQuery):
    tags = DataBase.Get_tags()
    markup = inline_keyborads.get_all_tags_keyboard(tags)
    await call.message.edit_text(text="Список всех тегов: ", reply_markup=markup)


# вся информация и возможные действия с одним тегом
@router.callback_query(F.data.startswith("tag information"))
async def get_tag_information(call: CallbackQuery):
    tag_name = call.data.split(' ')[2:]
    description = DataBase.Get_tag_description(' '.join(tag_name))[0][0]
    list_users = DataBase.Get_users_from_tag(' '.join(tag_name))
    users = ""
    markup = inline_keyborads.get_tag_information_keyboard(tag_name[0])
    for i in range(len(list_users)):
        users += "@" + " ".join(list(list_users[i]))
        users += "\n"
    await call.message.edit_text(text=f"Название тега: {' '.join(tag_name)}\n"
                                      f"Описание тега: {str(description) if description is not None else ''}\n"
                                      f"Участники тега:\n{users}",
                                 reply_markup=markup)


# вывод списка всех дней рождений
@router.callback_query(F.data == "birth_date")
async def get_birth_date(call: CallbackQuery):
    persons_with_birthday = DataBase.Get_users_with_birth_date()
    day = datetime.today()
    min_difference = math.inf
    next_persons = []  # список людей/человека у которого ближайший день рождения
    # поиск минимального количества дней до следующего дня рождения
    for i in range(len(persons_with_birthday)):
        next_birthday = datetime.strptime(persons_with_birthday[i][1], "%d.%m.%Y")
        if (next_birthday.month == day.month and next_birthday.day < day.day) or next_birthday.month < day.month:
            next_birthday = next_birthday.replace(year=day.year + 1)
        else:
            next_birthday = next_birthday.replace(year=day.year)
        if abs((next_birthday - day).days) <= min_difference:
            min_difference = abs((next_birthday - day).days)
    # поиск человека со ближайшим днём рождения
    for i in range(len(persons_with_birthday)):
        next_birthday = datetime.strptime(persons_with_birthday[i][1], "%d.%m.%Y")
        if (next_birthday.month == day.month and next_birthday.day < day.day) or next_birthday.month < day.month:
            next_birthday = next_birthday.replace(year=day.year + 1)
        else:
            next_birthday = next_birthday.replace(year=day.year)
        if abs((next_birthday - day).days) == min_difference:
            next_persons.append(persons_with_birthday[i][0])

    markup = inline_keyborads.get_birth_date_keyboard(next_persons)
    persons = ""
    persons_with_birthday.sort(key=sort_birthday)
    for i in persons_with_birthday:
        birthday = datetime.strptime(i[1], "%d.%m.%Y")
        persons += f"@{i[0]} {i[1]}"
        if ((birthday - day).days == min_difference and
            (birthday.month >= date.today().month and birthday.day >= date.today().day) or
                min_difference <= 7):
            persons += "🔜\n"
        elif ((date.today().month == birthday.month and date.today().day > birthday.day)
              or date.today().month > birthday.month):
            persons += "✅\n"
        else:
            persons += "⏳\n"
    await call.message.edit_text(text=f"Дни рождения:\n{persons}",
                                 reply_markup=markup)


@router.callback_query(F.data.startswith("accept_delete"))
async def option_of_life_tag(call: CallbackQuery):
    DataBase.Delete_tag(call.data.split(' ')[1])
    await get_all_tags(call)


@router.callback_query(F.data.startswith("activate_tag"))
async def activate_tag(call: CallbackQuery):
    answer = ""
    tag_name = call.data.split(' ')[1]
    users = DataBase.Get_users_from_tag(tag_name)
    for i in range(len(users)):
        answer += "@" + str(users[i][0]) + " "
    tag_description = DataBase.Get_tag_description(tag_name)[0]
    answer += str(tag_description[0])
    await call.bot.send_message(chat_id=CHAT_ID, text=answer, message_thread_id=99)


@router.callback_query(F.data.startswith("edit_users"))
async def start_edit_users(call: CallbackQuery):
    tag_name = call.data.split(' ')[1]
    markup = inline_keyborads.edit_users(tag_name)
    list_users = DataBase.Get_users_from_tag(tag_name)
    users = ""
    for i in range(len(list_users)):
        users += "@" + " ".join(list(list_users[i]))
        users += "\n"
    await call.message.edit_text(text=f"Название тега: {tag_name}\n"
                                      f"Участники тега:\n{users}", reply_markup=markup)


@router.callback_query(F.data.startswith("add_users"))
@router.callback_query(F.data.startswith("add_user"))
async def add_users(call: CallbackQuery):
    tag_name = call.data.split(' ')[1]
    user_on_button = call.data.split(' ')[2] if len(call.data.split(' ')) > 2 else None
    if user_on_button is not None:
        DataBase.Link_user_tag(user_on_button, tag_name)
    list_users_without_tag = DataBase.Get_users_not_in_tag(tag_name)
    markup = inline_keyborads.get_add_users(list_users_without_tag, tag_name)
    list_users_in_tag = DataBase.Get_users_from_tag(tag_name)
    users_in_tag = ""
    for i in range(len(list_users_in_tag)):
        users_in_tag += "@" + " ".join(list(list_users_in_tag[i]))
        users_in_tag += "\n"
    await call.message.edit_text(text=f"Название тега: {tag_name}\n"
                                      f"Участники тега:\n{users_in_tag}"
                                      f"Выберите кого хотите добавить:", reply_markup=markup)


@router.callback_query(F.data.startswith("delete_users") | F.data.startswith("delete_user"))
async def delete_users(call: CallbackQuery):
    tag_name = call.data.split(' ')[1]
    user_on_button = call.data.split(' ')[2] if len(call.data.split(' ')) > 2 else None
    if user_on_button is not None:
        DataBase.Delete_user_from_tag(user_on_button, tag_name)
    list_users_in_tag = DataBase.Get_users_from_tag(tag_name)
    markup = inline_keyborads.get_delete_users(list_users_in_tag, tag_name)
    users_in_tag = ""
    for i in range(len(list_users_in_tag)):
        users_in_tag += "@" + " ".join(list(list_users_in_tag[i]))
        users_in_tag += "\n"
    await call.message.edit_text(text=f"Название тега: {tag_name}\n"
                                      f"Участники тега:\n{users_in_tag}"
                                      f"Выберите кого хотите удалить", reply_markup=markup)


@router.message(~Command("start"), lambda message: message.chat.type == "private")
async def delete_message(message: Message):
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
