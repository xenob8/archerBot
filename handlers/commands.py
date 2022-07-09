from telebot import types
from states import EditStates, RegContext

from loader import bot, googleSheet

@bot.message_handler(commands=["edit"])
def editProfile(message: types.Message):
    bot.send_message(chat_id=message.chat.id, text="Введите новое имя")
    bot.set_state(user_id=message.from_user.id, state=EditStates.name)


@bot.message_handler(state=EditStates.name)
def getName(message: types.Message):
    bot.send_message(chat_id=message.chat.id, text="Введите новую фамилию")
    bot.set_state(user_id=message.from_user.id, state=EditStates.lastName)
    with bot.retrieve_data(user_id=message.from_user.id) as data:
        data[RegContext.NAME] = message.text


@bot.message_handler(state=EditStates.lastName)
def getLastName(message: types.Message):
    bot.set_state(user_id=message.from_user.id, state=EditStates.lastName)
    last_name = message.text
    with bot.retrieve_data(user_id=message.from_user.id) as data:
        if googleSheet.editUser(message.from_user.id, data[RegContext.NAME], last_name):
            bot.send_message(chat_id=message.chat.id, text="Вы успешно изменили инициалы")
        else:
            bot.send_message(chat_id=message.chat.id, text="Упс, что-то пошло не так")
    bot.delete_state(user_id=message.from_user.id)