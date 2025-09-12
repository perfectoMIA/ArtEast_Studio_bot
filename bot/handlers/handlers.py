from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.fsm.context import FSMContext
from datetime import datetime, date
import math

from bot.models import DataBase
import bot.keyboards.inline as inline_keyborads
from bot.states import BirthDate, Tag
from bot.handlers.fsm_handlers import menu

router = Router()


# новый пользователь в чате добавляется в бд.
@router.message(lambda message: message.new_chat_members is not None)
async def biba(message: Message):  # переименовать
    DataBase.Add_user(message.new_chat_members[0].id, message.new_chat_members[0].username)  # не робит
    spisok = DataBase.Get_users()
    await message.answer(f"Список пользователей: {spisok}")


# покинувший чат пользователь удаляется из бд
@router.message(lambda message: message.left_chat_member)
async def boba(message: Message):  # переименовать
    DataBase.Delete_user(message.left_chat_member.username)
    spisok = DataBase.Get_users()
    await message.answer(f"Список пользователей: {spisok}")


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
    descriprtion = DataBase.Get_tag_information(' '.join(tag_name))[0][0]
    list_users = DataBase.Get_users_from_tag(' '.join(tag_name))
    users = ""
    markup = inline_keyborads.get_tag_information_keyboard(tag_name[0])
    for i in range(len(list_users)):
        users += "@" + " ".join(list(list_users[i]))
        users += "\n"
    await call.message.edit_text(text=f"Название тега: {' '.join(tag_name)}\n"
                                      f"Описание тега: {str(descriprtion)}\n"
                                      f"Участники тега:\n{users}",
                                 reply_markup=markup)


# вывод списка всех дней рождений
@router.callback_query(F.data == "birth_date")
async def get_birth_date(call: CallbackQuery):
    persons = ""
    persons_with_birthday = DataBase.Get_users_with_birth_date()
    day = datetime.today()
    min_difference = math.inf
    next_persons = []
    for i in range(len(persons_with_birthday)):
        next_birthday = datetime.strptime(persons_with_birthday[i][1], "%d.%m.%Y")
        if (next_birthday.month == day.month and next_birthday.day < day.day) or next_birthday.month < day.month:
            next_birthday = next_birthday.replace(year=day.year + 1)
        else:
            next_birthday = next_birthday.replace(year=day.year)
        if abs((next_birthday - day).days) <= min_difference:
            min_difference = abs((next_birthday - day).days)

    for i in range(len(persons_with_birthday)):
        next_birthday = datetime.strptime(persons_with_birthday[i][1], "%d.%m.%Y")
        if (next_birthday.month == day.month and next_birthday.day < day.day) or next_birthday.month < day.month:
            next_birthday = next_birthday.replace(year=day.year + 1)
        else:
            next_birthday = next_birthday.replace(year=day.year)
        if abs((next_birthday - day).days) == min_difference:
            next_persons.append(persons_with_birthday[i][0])

    markup = inline_keyborads.get_birth_date_keyboard(next_persons)
    # сделать сортировку#################
    #persons_with_birthday.sort(key=lambda day: day[1])
    #print(persons_with_birthday)
    #####################################

    for i in persons_with_birthday:
        birthday = datetime.strptime(i[1], "%d.%m.%Y")
        persons += f'''@{i[0]} {i[1]} {'✅' if (date.today().month == birthday.month and
                                               date.today().day > birthday.day) or 
                                               date.today().month > birthday.month else '⏳'}\n'''
    await call.message.edit_text(text=f"Дни рождения:\n{persons}",
                                 reply_markup=markup)


@router.callback_query(F.data.startswith("accept_delete"))
async def option_of_life_tag(call: CallbackQuery):
    DataBase.Delete_tag(call.data.split(' ')[1])
    await get_all_tags(call)


@router.callback_query(F.data.startswith("activate_tag"))
async def activate_tag(call: CallbackQuery):
    answer = ""
    tag_name = tag_name = call.data.split(' ')[1]
    users = DataBase.Get_users_from_tag(tag_name)
    for i in range(len(users)):
        answer += "@" + str(users[i][0]) + " "
    tag_description = DataBase.Get_tag_information(tag_name)[0]
    answer += str(tag_description[0])
    await call.message.answer(answer)
