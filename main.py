import telebot
from telebot import custom_filters
from telebot.storage import StateMemoryStorage
from states import MyStates
from database import GoogleSheet
from keyboards import *
import config
import filters

# ADMINS = [317800531]
ADMINS = [480316781]
CREATOR_ID = 480316781

RETURN_DAYS_STATE = "-1"

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(config.BOT_TOKEN, state_storage=state_storage)

isShowDaysMarkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
recordExerciseButton = types.KeyboardButton("Записаться на занятие")
isShowDaysMarkup.add(recordExerciseButton)


@bot.callback_query_handler(func=days_callback.filter().check, state=MyStates.admindays, chat_id_callback=ADMINS)
def showHoursHandler(call: types.CallbackQuery):
    callback_data: dict = days_callback.parse(call.data)
    dayIndex = callback_data["dayIndex"]
    dayString = callback_data["dayStr"]
    with bot.retrieve_data(call.from_user.id) as data:
        data['dayIndexAdmin'] = dayIndex
        data['dayStringAdmin'] = dayString
    times, numbers = googleSheet.getTimeAndCountListsByDay(dayIndex)
    print(times)
    print(numbers)

    timesMarkup = getAdminTimesMarkUp(times)

    timesMarkup.add(types.InlineKeyboardButton(text="Вернуться к расписанию",
                                               callback_data=RETURN_DAYS_STATE))

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Выберите время для удаления" + dayString, reply_markup=timesMarkup)

    bot.set_state(call.from_user.id, MyStates.admintimes)


@bot.callback_query_handler(func=times_callback.filter().check, state=MyStates.admintimes, chat_id_callback=ADMINS)
def checkTypeHandler(call: types.CallbackQuery):
    callback: dict = times_callback.parse(call.data)
    with bot.retrieve_data(call.from_user.id) as data:
        data["timeIndexAdmin"] = callback["timeIndex"]
        data["timeStrAdmin"] = callback["timeStr"]
    deleteRecord(data["dayIndexAdmin"], data["timeIndexAdmin"])
    bot.delete_state(call.from_user.id)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Вы удалили занятие\n" + callback["timeStr"])


# Команда start
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


@bot.message_handler(text="Записаться на занятие")
def showDays(message: types.Message):
    # "Выберите день для записи":
    days = googleSheet.getAvailableDays()
    bot.send_message(chat_id=message.chat.id, text="Выберите день для записи", reply_markup=getDaysKeyMarkup(days))
    bot.set_state(message.chat.id, MyStates.days)


@bot.callback_query_handler(func=days_callback.filter().check, state=MyStates.days)
def showHoursHandler(call: types.CallbackQuery):
    callback_data: dict = days_callback.parse(call.data)
    dayIndex = callback_data["dayIndex"]
    dayString = callback_data["dayStr"]
    with bot.retrieve_data(call.from_user.id) as data:
        data['dayIndex'] = dayIndex
        data['dayString'] = dayString
    times, numbers = googleSheet.getTimeAndCountListsByDay(dayIndex)
    print(times)
    print(numbers)

    timesMarkup = getTimesMarkup(dayIndex, times, numbers)

    timesMarkup.add(types.InlineKeyboardButton(text="Вернуться к расписанию",
                                               callback_data=RETURN_DAYS_STATE))

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Доступное время на" + dayString, reply_markup=timesMarkup)

    bot.set_state(call.from_user.id, MyStates.times)


@bot.callback_query_handler(func=times_callback.filter().check, state=MyStates.times)
def checkTypeHandler(call: types.CallbackQuery):
    callback: dict = times_callback.parse(call.data)
    with bot.retrieve_data(call.from_user.id) as data:
        data["timeIndex"] = callback["timeIndex"]
        data["timeStr"] = callback["timeStr"]
    bot.set_state(call.from_user.id, MyStates.kinds_of_activity)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Выберите тип занятия\n" + callback["timeStr"],
                          reply_markup=chooseTypeMarkup())


@bot.callback_query_handler(func=types_activity_callback.filter().check, state=MyStates.kinds_of_activity)
def addStudentHandler(call: types.CallbackQuery):
    callback: dict = types_activity_callback.parse(call.data)
    type = callback["type"]
    with bot.retrieve_data(call.from_user.id) as data:
        dayIndex = data["dayIndex"]
        dayStr = data["dayString"]
        timeIndex = data["timeIndex"]
        timeStr = data["timeStr"]
        data["type"] = type
    print(timeIndex)

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text='Записываемся...')

    address, name = googleSheet.addStudent(type, dayIndex, timeIndex, call.from_user.id)

    if address:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Вы записаны на ' + dayStr + " " + timeStr,
                              reply_markup=cancelRecordMarkup(address))

        bot.set_state(call.from_user.id, MyStates.recordered)
        print(str(call.from_user.id) + "recordered")
        with bot.retrieve_data(call.from_user.id) as data:
            data["messageId"] = call.message.message_id
            data["cell"] = address
        # bot.send_message(MY_CHAT_ID, "На занятие " + call.message.text[18:] + " в " + timeValue + " записался\n" + name)
    else:
        bot.set_state(call.from_user.id, MyStates.days)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Ошибка записи, попробуйте другое время\n' + name,
                              reply_markup=getDaysKeyMarkup(googleSheet.getAvailableDays()))


@bot.callback_query_handler(func=cancel_record_callback.filter().check, state=MyStates.recordered)
def deleteUserHandler(call: types.CallbackQuery):
    callback: dict = cancel_record_callback.parse(call.data)

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Вы успешно отменили запись")
    # НЕ забыть про что у юзера может быть несколько сообщений и состояний
    bot.reset_data(call.from_user.id)
    bot.delete_state(call.from_user.id)
    googleSheet.deleteUser(callback["cell"])


@bot.callback_query_handler(func=lambda call: call.data == RETURN_DAYS_STATE)
def queryHandler(call: types.CallbackQuery):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Доступное время", reply_markup=getDaysKeyMarkup(googleSheet.getAvailableDays()))
    bot.set_state(call.from_user.id, MyStates.days)


def deleteRecord(dayIndex, timeIndex):
    ids = googleSheet.getUsersIdByTime(dayIndex, timeIndex)
    for id in ids:
        print(id)
        with bot.retrieve_data(id) as data:
            mess = data["messageId"]
            cell = data["cell"]

        bot.reset_data(id)
        bot.delete_state(id)
        googleSheet.deleteUser(cell)
        bot.send_message(id, text="ur acti canceled")
        bot.edit_message_text(chat_id=id, message_id=mess, text="Canceled")


@bot.message_handler(commands=["delete"], chat_id=ADMINS)
def showDays(message: types.Message):
    days = googleSheet.getAvailableDays()
    bot.send_message(chat_id=message.chat.id, text="Выберите день для удаления", reply_markup=getDaysKeyMarkup(days))
    bot.set_state(message.chat.id, MyStates.admindays)


googleSheet = GoogleSheet()
googleSheet.createFirstSheet("testArcher")
googleSheet.createSheetById("testArcher", 312817610)

bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.TextMatchFilter())
bot.add_custom_filter(custom_filters.ChatFilter())
bot.add_custom_filter(filters.ChatFilterCallback())

# Запускаем бота
bot.polling(none_stop=True, interval=0)
