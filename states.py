from telebot.handler_backends import State, StatesGroup

class MyStates(StatesGroup):
    name = State()
    surname = State()
    days = State()
    times = State()
    kinds_of_activity = State()
    recordered = State()
    admindays = State()
    admintimes = State()
