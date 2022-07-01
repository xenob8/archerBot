from telebot import types

from bot import getBot, getSheet
from constants import RETURN_DAYS_STATE
from keyboards import days_callback, getDaysKeyMarkup, times_callback, chooseTypeMarkup, types_activity_callback, \
    getTimesMarkup, cancelRecordMarkup, cancel_record_callback
from states import MyStates

bot = getBot()
googleSheet = getSheet()

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