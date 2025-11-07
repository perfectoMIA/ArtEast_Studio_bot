from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram import Bot

import asyncio
import re
from datetime import datetime

from bot.config import BOT_TOKEN, CHAT_ID
from bot.models import DataBase
from bot.states import BirthDate, Tag, MessageBirthday, EditName, EditDesicription, StartInGroup
import bot.keyboards.inline as inline_keyborads
import bot.passive_functions as passive_functions

router = Router()
bot = Bot(token=BOT_TOKEN)


# Обработчик команды /start только в личных сообщениях
@router.message(Command("start"), lambda message: message.chat.type == "private", StateFilter(None))
async def start_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:  # проверка пользователя на наличии в группе ArtEast studio (работает на всех кроме владельца бота)
        data = await bot.get_chat_member(chat_id=CHAT_ID, user_id=user_id)
        if data.status != "left":
            try:
                DataBase.Add_user(message.from_user.id, message.from_user.username)
                sent_message = await message.answer("Я успешно получил твои данные и занёс их в базу! "
                                                    "Введи свою дату рождения в формате: дд.мм.гггг")
            except Exception as e:
                print(type(e), e)
                return await menu(message)
            await state.set_state(BirthDate.birth_date)
        else:
            await message.answer("Вы не можете зарегестрироваться в этом Telegram bot, "
                                 "так как не являетесь участником группы ArtEast studio")
    except Exception as e:  # если пользователя нет в нужной группе, то мы не регестрируем его
        print(type(e), e)
        await message.answer("Вы не можете зарегестрироваться в этом Telegram bot, "
                             "так как не являетесь участником группы ArtEast studio")


# /start в группе
@router.message(Command("start"), StateFilter(None))
async def start_in_group(message: Message, state: FSMContext):
    if DataBase.Get_user_by_id(message.from_user.id):
        await state.set_state(StartInGroup.menu)
        await state.update_data(message_id=message.message_id)
        await state.update_data(chat_id=message.chat.id)
        return await menu(message, state)
    else:
        sent_message = await message.answer("Вас нет в базе данных, "
                                            "перейдите в личные сообщения с ботом и пройдите регистрацию.")
        await asyncio.sleep(60)
        await message.delete()
        await sent_message.delete()


@router.message(BirthDate.birth_date)
async def get_birth_date(message: Message, state: FSMContext = None):
    birthdate_regex = re.compile(
        r"^(0[1-9]|[12][0-9]|3[01])\."
        r"(0[1-9]|1[0-2])\."
        r"(19[0-9]{2}|20(0[0-9]|1[0-9]|2[0-5]))$"
    )
    date = message.text
    try:
        if birthdate_regex.match(date) is not None and datetime.strptime(date, "%d.%m.%Y"):
            try:
                DataBase.Add_birth_date(date, message.from_user.id)
                await message.answer("Ваш день рождения добавлен в базу!")
                await state.clear()
            except Exception as e:
                print(type(e), e)
                await message.answer("Ваш день рождения уже был в базе!")
                await state.clear()
            finally:
                return await menu(message)
        else:
            await message.answer(
                "Дата которую вы ввели неправильная, проверьте формат ввода или корректность даты и "
                "введите свою дату рождения в формате: дд.мм.гггг")
    except Exception as e:
        print(type(e), e)
        await message.answer(
            "Дата которую вы ввели неправильная, проверьте формат ввода или корректность даты и "
            "введите свою дату рождения в формате: дд.мм.гггг")


@router.callback_query((F.data == "start") | (F.data == "stop_creating_tag"))
async def menu(update: Message | CallbackQuery, state: FSMContext = None):
    if state is not None:
        data = await state.get_data()
        if data and isinstance(data, dict) and data.get("chat_id") and data.get("message_id"):
            await bot.delete_message(
                chat_id=data["chat_id"],
                message_id=data["message_id"]
            )
        await state.clear()
    markup = inline_keyborads.get_menu_keyboard()
    flag_type_chat = False
    # если мы находимся в личных сообщениях
    if isinstance(update, CallbackQuery) and update.message.chat.type == "private":
        flag_type_chat = True
    elif isinstance(update, Message) and update.chat.type == "private":
        flag_type_chat = True
    if DataBase.Check_admin(update.from_user.id) and flag_type_chat:
        # если пользователь админ, то добавляем доп кнопки
        markup.inline_keyboard.append([InlineKeyboardButton(  # рассылка о заполнении рабочих часов
            text="Список учёта часов",
            callback_data="watch_tracking_day")])
        markup.inline_keyboard.append([InlineKeyboardButton(  # рассылка о сдачи денег на дни рождения
            text="Общая рассылка",
            callback_data="spam_about_money"
        )])
    text = "Выбери что ты хочешь сделать:"
    if isinstance(update, CallbackQuery):
        await update.message.edit_text(text=text, reply_markup=markup, )
    else:
        await update.answer(text=text, reply_markup=markup)


# пользователь вводит название тега
@router.callback_query(F.data == "create_tag", StateFilter(None))
async def create_tag(call: CallbackQuery, state: FSMContext):
    markup = inline_keyborads.stop_creating_tag()
    try:
        await call.message.edit_text("Введите название тега:", reply_markup=markup)
        await state.update_data(message_id=call.message.message_id)
        await state.set_state(Tag.name)
    except Exception as e:
        print(type(e), e)


# пользователь вводит описание тега
@router.message(Tag.name)
async def create_tag_name(message: Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.delete()
    tag_name_regex = re.compile(r"^[а-яА-ЯёЁ\w]+$")
    markup = inline_keyborads.stop_creating_tag()
    if tag_name_regex.match(name) is not None and DataBase.Check_tag_name(name) is False:
        await message.bot.edit_message_text(f'Название тега: {(await state.get_data())["name"]}\n'
                                            'Введите описание тега. Если хотите пропустить этот пункт введите "."',
                                            reply_markup=markup,
                                            chat_id=message.chat.id, message_id=(await state.get_data())['message_id'])
        await state.set_state(Tag.description)
    else:
        await message.edit_text("Вы ввели некорреткное название тега или тег с таким названием уже существует. "
                                "попытайтесь снова:", reply_markup=markup)


# пользователь выбирает участников тега
@router.message(Tag.description)
async def create_tag_description(message: Message, state: FSMContext):
    description = message.text
    try:
        (await state.get_data())["description"]
    except KeyError as error:
        await state.update_data(description=description)
        markup = inline_keyborads.get_all_name_users()
        users = DataBase.Get_users()
        text = (f"Название тега: {(await state.get_data())['name']}\n"
                f"Описание тега: {(await state.get_data())['description']}\n"
                f"Участники тега:\n")
        text += "Выберите участников тега:\n"
        await message.bot.edit_message_text(text=text, reply_markup=markup, chat_id=message.chat.id,
                                            message_id=(await state.get_data())['message_id'])
    await state.update_data(users="")
    await message.delete()


@router.callback_query(F.data.startswith("user"))
async def add_users_in_tag(call: CallbackQuery, state: FSMContext):
    users = list()
    tmp = (await state.get_data())["users"]
    if type(list) is str:
        tmp = tmp.split(' ')
        for t in tmp:
            if t != '':
                users.append(t)
    else:
        for t in tmp:
            users.append(t)

    users.append(call.data.split(' ')[1])
    users_not_in_list = DataBase.Get_users_not_in_the_list(users)
    await state.update_data(users=users)
    text = (f"Название тега: {(await state.get_data())['name']}\n"
            f"Описание тега: {(await state.get_data())['description']}\n"
            f"Участники тега:\n")
    for user in users:
        text += "@" + user + "\n"
    text += "Выберите участников тега:\n"
    markup = inline_keyborads.get_users_in_list(users_not_in_list)
    await call.message.edit_text(text=text, reply_markup=markup)


@router.callback_query(F.data == "finish_create_tag")
async def finish_create_tag(call: CallbackQuery, state: FSMContext):
    tag_data = await state.get_data()
    DataBase.Create_tag((tag_data["name"]))
    if tag_data["description"] != ".":
        DataBase.Add_description_to_tag(tag_data["name"], tag_data["description"])

    users = tag_data["users"]
    for user in users:
        DataBase.Link_user_tag(user, tag_data["name"])
    await state.clear()
    await menu(call)


@router.callback_query(F.data.startswith("message_about_birthday"))
async def send_message_birthday(call: CallbackQuery, state: FSMContext):
    user_with_birthday = call.data.split(' ')[1]
    await state.update_data(birthday_boy=user_with_birthday)
    await state.set_state(MessageBirthday.text)
    await call.message.answer(f"Введите сообщение для всех пользователей, кроме именинника ({user_with_birthday}).")


@router.message(MessageBirthday.text)
async def send_message_birthday(message: Message, state: FSMContext, bot: Bot):
    markup = inline_keyborads.accept_event()
    birthday_boy = (await state.get_data())["birthday_boy"]
    users = DataBase.Get_users_for_send_message_about_birthday(birthday_boy.replace('@', ''))
    for user in users:
        await bot.send_message(chat_id=int(user[0]), text=message.text)
    await state.update_data(users=users)
    await state.update_data(text=message.text)
    await message.answer(f'Ваше сообщение: "{message.text}" было отправлено всем кроме именинника ({birthday_boy}).',
                         reply_markup=markup)
    await state.clear()


@router.callback_query(F.data.startswith("delete_tag"))
async def delete_tag(call: CallbackQuery):
    tag_name = (call.data.split(' '))[1]
    markup = inline_keyborads.choice_of_life_tag(tag_name)
    await call.message.edit_text(text=f"Вы действительно хотите удалить тег: {tag_name}", reply_markup=markup)


@router.callback_query(F.data.startswith("change_tag"))
async def change_tag(call: CallbackQuery):
    tag_name = (call.data.split(' '))[1]
    description = DataBase.Get_tag_description(tag_name)
    markup = inline_keyborads.get_tag_settings(tag_name)
    list_users = DataBase.Get_users_from_tag(tag_name)
    users = ""
    for i in range(len(list_users)):
        users += "@" + " ".join(list(list_users[i]))
        users += "\n"
    text = (f"Название тега: {tag_name}\n"
            f"Описание тега: {str(description[0][0]) if description is not None else ''}\n"
            f"Участники тега:\n{users}")
    await call.message.edit_text(text=text, reply_markup=markup)


@router.callback_query(F.data.startswith("edit_name"))
async def start_edit_name(call: CallbackQuery, state: FSMContext):
    tag_name = call.data.split(' ')[1]
    markup = inline_keyborads.back_to_settings(tag_name)
    await call.message.edit_text(text=f"Старое название тега: {tag_name}\n"
                                      "Введите новое название: ", reply_markup=markup)
    await state.update_data(message_id=call.message.message_id)
    await state.update_data(old_tag_name=tag_name)
    await state.set_state(EditName.name)


@router.message(EditName.name)
async def edit_name(message: Message, state: FSMContext):
    tag_name = message.text
    tag_name_regex = re.compile(r"^[а-яА-ЯёЁ\w]+$")
    await message.delete()

    if tag_name_regex.match(tag_name) is not None and DataBase.Check_tag_name(tag_name) is False:
        DataBase.Rename_tag(old_tag=(await state.get_data())["old_tag_name"], new_tag=tag_name)
        await passive_functions.back_to_tag_information(tag_name=tag_name, message=message, state=state)
        await state.clear()
    else:
        markup_for_else = inline_keyborads.back_to_settings(tag_name)
        await message.edit_text("Вы ввели некорреткное название тега или тег с таким названием уже существует. "
                                "попытайтесь снова:", reply_markup=markup_for_else)


@router.callback_query(F.data.startswith("edit_description"))
async def start_edit_description(call: CallbackQuery, state: FSMContext):
    tag_name = call.data.split(' ')[1]
    description = DataBase.Get_tag_description(tag_name)
    markup = inline_keyborads.back_to_settings(tag_name)
    await state.update_data(message_id=call.message.message_id)
    await call.message.edit_text(text=f"Название тега: {tag_name}\n"
                                      f"Старое описание тега: {description[0][0]}\n"
                                      'Введите новое описание тега. Если хотите тег без описания введите "."',
                                 reply_markup=markup)
    await state.update_data(tag_name=tag_name)
    await state.set_state(EditDesicription.description)


@router.message(EditDesicription.description)
async def edit_description(message: Message, state: FSMContext):
    tag_name = (await state.get_data())["tag_name"]
    description = message.text
    DataBase.Edit_description(tag_name=tag_name, new_description=description)
    await passive_functions.back_to_tag_information(tag_name=tag_name, message=message, state=state)
    await message.delete()
    await state.clear()
