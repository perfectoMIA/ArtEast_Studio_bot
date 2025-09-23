from aiogram.fsm.state import StatesGroup, State


class BirthDate(StatesGroup):
    birth_date = State()


class Tag(StatesGroup):
    name = State()
    description = State()
    users = State()


class MessageBirthday(StatesGroup):
    text = State()


class EditName(StatesGroup):
    name = State()


class EditDesicription(StatesGroup):
    description = State()
