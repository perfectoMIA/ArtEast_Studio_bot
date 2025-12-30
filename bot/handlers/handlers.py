from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram import F, Bot
from datetime import datetime, date
import math
from aiogram.filters import Command

from bot.models import DataBase
import bot.keyboards.inline as inline_keyborads
from bot.passive_functions import sort_birthday
from bot.config import CHAT_ID, RECEIPT_RECIPIENT

router = Router()


# новый пользователь в чате должен пройти регистрацию в боте (бот не может первым писать в лс).
@router.message(lambda message: message.new_chat_members is not None)
async def send_message_new_members(message: Message):
    for i in range(len(message.new_chat_members)):
        await message.answer(f"Йо-хо-хо, @{message.new_chat_members[i].username} "
                             f"ты оказался достоин добавления в эту группу! "
                             f"Перейди в личные сообщения со мной и пройди регистрацию для дальнейшей работы в студии.")


# покинувший чат пользователь удаляется из бд
@router.message(lambda message: message.left_chat_member)
async def boba(message: Message):  # переименовать
    DataBase.Delete_user(message.left_chat_member.username)


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
    i = 0
    while i < len(persons_with_birthday):  # удаляем всех пользователей без др
        if persons_with_birthday[i][1] == "None":
            persons_with_birthday.pop(i)
        else:
            i += 1
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


# если пользователь скидывает фото или документ в бота об оплате
@router.message(F.content_type.in_({'photo', 'document'}), lambda message: message.chat.type == "private")
async def get_check(message: Message):
    # если пользователь уже скинул чек, то просто удаляем его сообщение
    if DataBase.Check_sent_money_person(message.from_user.id) is True:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    else:
        chat_id = RECEIPT_RECIPIENT
        if message.content_type == 'photo':
            await message.bot.send_photo(chat_id=chat_id, photo=message.photo[-1].file_id,
                                         caption=f"Чек от @{message.from_user.username}")
        elif message.content_type == 'document':
            await message.bot.send_document(chat_id=chat_id, document=message.document.file_id,
                                            caption=f"Чек от @{message.from_user.username}")
        DataBase.Sent_money(message.from_user.id)


# удаление неперехваченных сообщений
@router.message(~Command("start"), lambda message: message.chat.type == "private")
async def delete_message(message: Message):
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@router.callback_query(F.data.startswith("spam_yes"))
async def Change_Spam_on_yes(call: CallbackQuery):
    day = call.data.split(' ')[1]
    DataBase.Change_state_in_Spam(state="Заполнил", day=day, id_user=call.from_user.id)
    await call.message.delete()


@router.callback_query(F.data.startswith("spam_no"))
async def Change_Spam_on_no(call: CallbackQuery):
    day = call.data.split(' ')[1]
    DataBase.Change_state_in_Spam(state="Не работал", day=day, id_user=call.from_user.id)
    await call.message.delete()


@router.callback_query(F.data == "watch_tracking_day")
async def Get_watch_tracking_days(call: CallbackQuery):
    markup = inline_keyborads.Get_watch_tracking_days()
    await call.message.edit_text(text="Выберите день:", reply_markup=markup)


@router.callback_query(F.data.startswith("day"))
async def Get_watch_tracking_list(call: CallbackQuery):
    markup = inline_keyborads.Get_watch_tracking_list()
    day = call.data.split(' ')[1]  # название столбца
    text = f"Список учёта часов за {day}:\n"
    users = DataBase.Get_tracking_users(day)
    for user in users:
        text += f"@{user[0]} - {user[1]} "
        if user[1] == "Не заполнял":
            text += "❌\n"
        elif user[1] == "Заполнил":
            text += "✅\n"
        elif user[1] == "Не работал":
            text += "💤\n"
    await call.message.edit_text(text=text, reply_markup=markup)


# рассылка о скидывании денег
@router.callback_query(F.data == "spam_about_money")
async def Settings_pam_about_money(call: CallbackQuery, bot: Bot):
    pass


@router.callback_query(F.data == "edit_users_lists")
async def select_lists(call: CallbackQuery):
    pass

@router.callback_query(F.data == "delete_users_from_bot")
async def delete_user_from_bot(call: CallbackQuery):
    pass