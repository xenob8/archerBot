from telebot import types

import constants
from bot import getBot, getSheet
from constants import RETURN_DAYS_STATE
from keyboards import days_callback, getDaysKeyMarkup, times_callback, chooseTypeMarkup, types_activity_callback, \
    getTimesMarkup, cancelRecordMarkup, cancel_record_callback
from states import MyStates, Context

bot = getBot()
googleSheet = getSheet()


@bot.message_handler(text="test", state=MyStates.days)
def test(message: types.Message, ):
    with bot.retrieve_data(message.from_user.id) as data:
        print(data)

    bot.set_state(message.from_user.id, None)

    with bot.retrieve_data(message.from_user.id) as data:
        print(data)

        # print(data["lol"])


@bot.callback_query_handler(func=days_callback.filter().check, state=MyStates.days)
def showHoursHandler(call: types.CallbackQuery):
    callback_data: dict = days_callback.parse(call.data)
    dayIndex = callback_data["dayIndex"]
    dayString = callback_data["dayStr"]
    with bot.retrieve_data(call.from_user.id) as data:
        data: dict[int, str]
        data[Context.DAY_INDEX] = dayIndex
        data[Context.DAY_STRING] = dayString
    times, numbers = googleSheet.getTimeAndCountListsByDay(dayIndex)
    print(times)
    print(numbers)

    timesMarkup = getTimesMarkup(dayIndex, times, numbers)

    timesMarkup.add(types.InlineKeyboardButton(text="Вернуться к расписанию",
                                               callback_data=RETURN_DAYS_STATE))

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Доступное время на " + dayString, reply_markup=timesMarkup)

    bot.set_state(call.from_user.id, MyStates.times)


@bot.callback_query_handler(func=lambda call: call.data == RETURN_DAYS_STATE)
def returnToDays(call: types.CallbackQuery):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Доступное время", reply_markup=getDaysKeyMarkup(googleSheet.getAvailableDays()))
    bot.set_state(call.from_user.id, MyStates.days)


@bot.callback_query_handler(func=lambda call: call.data == constants.EXIT, state=[MyStates.days, MyStates.admindays])
def exit(call: types.CallbackQuery):
    bot.delete_message(chat_id=call.message.chat.id,
                       message_id=call.message.message_id)
    bot.delete_state(call.from_user.id)


@bot.message_handler(state=MyStates.days)
def showHoursHandler(call: types.CallbackQuery):
    bot.send_message(call.from_user.id, text="Выберите нужную кнопку")


@bot.callback_query_handler(func=times_callback.filter().check, state=MyStates.times)
def checkTypeHandler(call: types.CallbackQuery):
    callback: dict = times_callback.parse(call.data)
    with bot.retrieve_data(call.from_user.id) as data:
        data: dict[int, Context]
        data[Context.TIME_INDEX] = callback["timeIndex"]
        data[Context.TIME_STRING] = callback["timeStr"]
    bot.set_state(call.from_user.id, MyStates.kinds_of_activity)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Выберите тип занятия\n" + callback["timeStr"],
                          reply_markup=chooseTypeMarkup())


@bot.message_handler(state=MyStates.times)
def checkTypeHandler(call: types.CallbackQuery):
    bot.send_message(call.from_user.id, text="Выберите нужную кнопку")


@bot.callback_query_handler(func=types_activity_callback.filter().check, state=MyStates.kinds_of_activity)
def addStudentHandler(call: types.CallbackQuery):
    callback: dict = types_activity_callback.parse(call.data)
    type = callback["type"]
    with bot.retrieve_data(call.from_user.id) as data:
        data: dict[int, str]
        dayIndex = data[Context.DAY_INDEX]
        dayStr = data[Context.DAY_STRING]
        timeIndex = data[Context.TIME_INDEX]
        timeStr = data[Context.TIME_STRING]
        data[Context.TYPE] = type

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text='Записываемся...')

    address, name = googleSheet.addStudent(type, dayIndex, timeIndex, call.from_user.id)

    if address:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Вы записаны на ' + dayStr + " " + timeStr,
                              reply_markup=cancelRecordMarkup(address))

        bot.delete_state(call.from_user.id)
        print(str(call.from_user.id) + "recordered")

        bot.send_message(constants.CREATOR_ID, "На занятие " + dayStr + " в " + timeStr + " записался\n" + name)
        googleSheet.addRecord(userId=call.from_user.id, dayIndex=dayIndex, timeIndex=timeIndex,
                              messageId=call.message.id)
    else:
        bot.set_state(call.from_user.id, MyStates.days)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Ошибка записи, попробуйте другое время\n' + name,
                              reply_markup=getDaysKeyMarkup(googleSheet.getAvailableDays()))


@bot.message_handler(state=MyStates.kinds_of_activity)
def checkTypeHandler(call: types.CallbackQuery):
    bot.send_message(call.from_user.id, text="Выберите нужную кнопку")


@bot.callback_query_handler(func=cancel_record_callback.filter().check)
def deleteUserHandler(call: types.CallbackQuery):
    callback: dict = cancel_record_callback.parse(call.data)

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Вы успешно отменили запись")

    googleSheet.deleteUser(callback["cell"])
    googleSheet.deleteRecordByMessageId(call.message.id)


@bot.message_handler(text="Записаться на занятие")
def showDays(message: types.Message):
    # "Выберите день для записи":
    days = googleSheet.getAvailableDays()
    bot.send_message(chat_id=message.chat.id, text="Выберите день для записи", reply_markup=getDaysKeyMarkup(days))
    bot.set_state(message.chat.id, MyStates.days)
