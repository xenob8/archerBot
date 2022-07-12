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
    DATE = 10
    DAY_INDEX = 0
    DAY_STRING = 1
    TIME_INDEX = 2
    TIME_STRING = 3
    TYPE = 4
    CELL = 5
    ADMIN_DAY_INDEX = 6
    ADMIN_DAY_STRING = 7
    ADMIN_TIME_INDEX = 8
    ADMIN_TIME_STRING = 9

class RegContext(IntEnum):
    NAME = 0
    LAST_NAME = 1