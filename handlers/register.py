import keyboards
from constants import ADMINS
from loader import bot, googleSheet
from states import RegisterStates
from telebot.types import Message



@bot.message_handler(commands=["start"], chat_id=ADMINS)
def startAdmin(message: Message):
    firstName = message.from_user.first_name
    lastName = message.from_user.last_name
    bot.send_message(message.chat.id, 'Привет, админ ' + ' '.join(filter(None, [firstName, lastName])))
    if googleSheet.isUserExist(message.from_user.id):
        bot.send_message(chat_id=message.chat.id, text="Вы уже зарегестрированы",
                         reply_markup=keyboards.adminDefaultMarkup())
        return
    bot.send_message(message.chat.id, "Начинаем регистрацию")

    bot.set_state(message.from_user.id, RegisterStates.name, message.chat.id)
    bot.send_message(message.chat.id, "Введите ваше имя(без фамилии)")


@bot.message_handler(commands=["start"])
def start(message: Message):
    firstName = message.from_user.first_name
    lastName = message.from_user.last_name
    bot.send_message(message.chat.id, 'Привет, ' + ' '.join(filter(None, [firstName, lastName])))
    if googleSheet.isUserExist(message.from_user.id):
        bot.send_message(chat_id=message.chat.id, text="Вы уже зарегестрированы",
                         reply_markup=keyboards.isShowDaysMarkup)
        return
    bot.send_message(message.chat.id, "Начинаем регистрацию")

    bot.set_state(message.from_user.id, RegisterStates.name, message.chat.id)
    bot.send_message(message.chat.id, "Введите ваше имя(без фамилии)")

@bot.message_handler(state="*", commands=['cancel'])
def any_state(message: Message):
    """
    Cancel state
    """
    bot.send_message(message.chat.id, "Your state was cancelled.")
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state=RegisterStates.name)
def getName(message: Message):
    """
    State 1. Will process when user's state is MyStates.name.
    """
    bot.send_message(message.chat.id, f'Введите фамилию')
    bot.set_state(message.from_user.id, RegisterStates.lastName, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['name'] = message.text




@bot.message_handler(state=RegisterStates.lastName, chat_id=ADMINS)
def getLastName(message: Message):
    """
    State 2. Will process when user's state is MyStates.surname.
    """
    bot.send_message(message.chat.id, "Регистрация пройдена", reply_markup=keyboards.adminDefaultMarkup())

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['surname'] = message.text

    googleSheet.registerUser(data['name'], data['surname'], message.from_user.id)
    bot.delete_state(message.from_user.id, message.chat.id)

@bot.message_handler(state=RegisterStates.lastName)
def getLastName(message: Message):
    """
    State 2. Will process when user's state is MyStates.surname.
    """
    bot.send_message(message.chat.id, "Регистрация пройдена", reply_markup=keyboards.isShowDaysMarkup)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['surname'] = message.text

    googleSheet.registerUser(data['name'], data['surname'], message.from_user.id)
    bot.delete_state(message.from_user.id, message.chat.id)

#
# @bot.message_handler(state=RegisterStates.type)
# def getActivityType(message: Message):
#     bot.send_message(message.chat.id, "Регистрация пройдена", reply_markup=isShowDaysMarkup)
