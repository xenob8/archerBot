from enum import Enum, IntEnum

from telebot.handler_backends import State, StatesGroup

class EditStates(StatesGroup):
    name = State()
    lastName = State()

class RegisterStates(StatesGroup):
    name = State()
    lastName = State()
    type = State()

class MyStates(StatesGroup):
    name = State()
    surname = State()
    days = State()
    times = State()
    kinds_of_activity = State()
    recordered = State()
    admindays = State()
    admintimes = State()


class Context(IntEnum):
    RECORDS = 0
    AUTH_DATE = 1
    DATE = 2
    USER_NAME = 3

class RegContext(IntEnum):
    NAME = 0
    LAST_NAME = 1