from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter

import re
from datetime import datetime

from bot.models import DataBase
from bot.states import BirthDate, Tag, MessageBirthday
import bot.keyboards.inline as inline_keyborads

router = Router()


# Обработчик команды /start только в личных сообщениях
@router.message(Command("start"), lambda message: message.chat.type == "private", StateFilter(None))
async def start_handler(message: Message, state: FSMContext):
    try:
        DataBase.Add_user(message.from_user.id, message.from_user.username)
        await message.answer("Я успешно получил твои данные и занёс их в базу! "
                             "Введи свою дату рождения в формате: дд.мм.гггг")
    except Exception as e:
        print(type(e), e)
        return await menu(message)
    await state.set_state(BirthDate.birth_date)


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
        await state.clear()
        print(await state.get_data())
    markup = inline_keyborads.get_menu_keyboard()
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
                                            'Введите описание тега. Если хотите пропустить этот пункт введите "нет":',
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
    await state.update_data(description=description)
    await state.update_data(users="")
    await message.delete()
    markup = inline_keyborads.get_all_name_users()
    users = DataBase.Get_users()
    text = (f"Название тега: {(await state.get_data())['name']}\n"
            f"Описание тега: {(await state.get_data())['description']}\n"
            "Выберите участников тега:\n")
    for user in users:
        text += "@" + str(user[0]) + "\n"
    await message.bot.edit_message_text(text=text, reply_markup=markup, chat_id=message.chat.id,
                                        message_id=(await state.get_data())['message_id'])


@router.callback_query(F.data.startswith("user"))
async def add_users_in_tag(call: CallbackQuery, state: FSMContext):
    users = (await state.get_data())["users"]
    users += call.data.split(' ')[1] + " "
    await state.update_data(users=users)


@router.callback_query(F.data == "finish_create_tag")
async def finish_create_tag(call: CallbackQuery, state: FSMContext):
    tag_data = await state.get_data()
    print(tag_data)
    DataBase.Create_tag((tag_data["name"]))
    if tag_data["description"] != "нет":
        DataBase.Add_description_to_tag(tag_data["name"], tag_data["description"])
    users = tag_data["users"].strip().split(' ')
    for user in users:
        DataBase.Link_user_tag(user, tag_data["name"])
    await state.clear()
    await menu(call)


@router.message(MessageBirthday.text)
async def send_message_birthday(message: Message, state: FSMContext, call: CallbackQuery):

    await message.answer("Ваше сообщение было отправлено всем кроме пользователя у которого будет день рождения")
    await state.clear()


@router.callback_query(F.data.startswith("delete_tag"))
async def delete_tag(call: CallbackQuery):
    tag_name = (call.data.split(' '))[1]
    markup = inline_keyborads.choice_of_life_tag(tag_name)
    await call.message.edit_text(text=f"Вы действительно хотите удалить тег: {tag_name}", reply_markup=markup)
