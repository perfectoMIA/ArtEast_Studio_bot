from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.models import DataBase


# стартовое меню
def get_menu_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="просмотреть все теги", callback_data="all_tags")],
        [InlineKeyboardButton(text="создать тег", callback_data="create_tag")],
        [InlineKeyboardButton(text="дни рождения", callback_data="birth_date")]])
    return markup


# показать все теги
def get_all_tags_keyboard(tags: list) -> InlineKeyboardMarkup:
    list_buttons = list()
    for i in range(len(tags)):
        list_buttons.append([InlineKeyboardButton(text=tags[i][0], callback_data=f"tag information {tags[i][0]}")])
    list_buttons.append([InlineKeyboardButton(text="назад", callback_data="start")])
    markup = InlineKeyboardMarkup(inline_keyboard=list_buttons)
    return markup


# настройки тега
def get_tag_information_keyboard(tag_name: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Активировать тег", callback_data=f"activate_tag {tag_name}")],
        [InlineKeyboardButton(text="Изменть тег", callback_data=f"change_tag {tag_name}")],
        [InlineKeyboardButton(text="Удалить тег", callback_data=f"delete_tag {tag_name}")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_all_tags")]
    ])
    return markup


# ближайшие к дню рождения люди
def get_birth_date_keyboard(persons: list) -> InlineKeyboardMarkup:
    name = ""
    print(persons)
    for i in range(len(persons)):
        name += f"@{persons[i]}"
        if i + 1 < len(persons):
            name += " и "
    print(name)
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Написать информацию по дню рождения {name}",
                              callback_data=f"message_about_birthday {name}")],
        [InlineKeyboardButton(text="Назад", callback_data="start")]
    ])
    return markup


# прекращение создания тега
def stop_creating_tag() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="прекратить создание тега",
                                                                         callback_data="stop_creating_tag")]])
    return markup


# список всех пользователей
def get_all_name_users() -> InlineKeyboardMarkup:
    users = DataBase.Get_users()
    markup = InlineKeyboardMarkup(inline_keyboard=[[]])
    for user in users:
        markup.inline_keyboard.append([InlineKeyboardButton(text=f"@{user[0]}", callback_data=f"user {user[0]}")])
    markup.inline_keyboard.append([InlineKeyboardButton(text="закончить выбор",
                                                        callback_data="finish_create_tag")])
    markup.inline_keyboard.append([InlineKeyboardButton(text="прекратить создание тега",
                                                        callback_data="stop_creating_tag")])
    return markup


# выбор об удалении или оставлении тега
def choice_of_life_tag(tag_name: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data=f"accept_delete {tag_name}")],
        [InlineKeyboardButton(text="Нет", callback_data=f"back_to_all_tags")]
    ])
    return markup


def accept_event() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ОК", callback_data="start")]])
    return markup
