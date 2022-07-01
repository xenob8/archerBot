from bot import getBot, getSheet
from states import MyStates
from keyboards import isShowDaysMarkup

bot = getBot()
googleSheet = getSheet()

@bot.message_handler(commands=["start"])
def start(message):
    firstName = message.from_user.first_name
    lastName = message.from_user.last_name
    bot.send_message(message.chat.id, 'Привет, ' + ' '.join(filter(None, [firstName, lastName])))
    bot.send_message(message.chat.id, "Начинаем регистрацию")

    bot.set_state(message.from_user.id, MyStates.name, message.chat.id)
    bot.send_message(message.chat.id, "Введите ваше имя(без фамилии)")


@bot.message_handler(state="*", commands=['cancel'])
def any_state(message):
    """
    Cancel state
    """
    bot.send_message(message.chat.id, "Your state was cancelled.")
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state=MyStates.name)
def name_get(message):
    """
    State 1. Will process when user's state is MyStates.name.
    """
    bot.send_message(message.chat.id, f'Введите фамилию')
    bot.set_state(message.from_user.id, MyStates.surname, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['name'] = message.text


@bot.message_handler(state=MyStates.surname)
def registationEnd(message):
    """
    State 2. Will process when user's state is MyStates.surname.
    """
    bot.send_message(message.chat.id, "Регистрация пройдена", reply_markup=isShowDaysMarkup)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['surname'] = message.text

    googleSheet.registerUser(data['name'], data['surname'], message.from_user.id)
    bot.delete_state(message.from_user.id, message.chat.id)