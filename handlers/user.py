from telebot import types

import constants
import keyboards
import utils
from loader import bot, googleSheet
from constants import RETURN_DAYS_STATE
from keyboards import *
from record import Record
from states import MyStates, Context
from utils import *

MAX_AUTH_TIME_IN_MIN = 2

@bot.message_handler(state=[MyStates.days, MyStates.times, MyStates.kinds_of_activity])
def showHoursHandler(call: types.CallbackQuery):
    bot.send_message(call.from_user.id, text="Закончите предыдущую запись")

@bot.message_handler(text="Записаться на занятие")
def showDays(message: types.Message):
    # "Выберите день для записи":
    userName = googleSheet.getUserNameById(message.from_user.id)
    avalRecords = getAvaliableRecords(googleSheet.getAllRecords(), userName)
    dailyRecords = getRecordsWithDiffDays(avalRecords)

    bot.send_message(chat_id=message.chat.id, text="Выберите день для записи",
                     reply_markup=getDaysKeyMarkupByRecords(dailyRecords))

    bot.set_state(message.chat.id, MyStates.days)
    with bot.retrieve_data(user_id=message.from_user.id) as data:
        data[Context.AUTH_DATE] = datetime.now()
        data[Context.RECORDS] = avalRecords
        data[Context.USER_NAME] = userName


@bot.callback_query_handler(func=lambda call: call.data == constants.EXIT, state=MyStates.days)
def exitToMainMenu(call: types.CallbackQuery):
    bot.delete_message(chat_id=call.from_user.id, message_id=call.message.id)
    bot.delete_state(call.from_user.id)


@bot.callback_query_handler(func=recordsCallBack.filter().check, state=MyStates.days)
def showHoursHandler(call: types.CallbackQuery):
    callback_data: dict = recordsCallBack.parse(call.data)
    dayStringFormat = callback_data["dayFormatted"]
    date = utils.dayStringToDatetime(dayStringFormat)

    with bot.retrieve_data(user_id=call.from_user.id) as data:
        records = data[Context.RECORDS]
        data[Context.DATE] = date

    records = getRecordsByDay(records, date)
    timesMarkup = getTimesMarkupWithRecords(records)

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Доступное время на " + utils.dateToHumanString(date), reply_markup=timesMarkup)

    bot.set_state(call.from_user.id, MyStates.times)


@bot.callback_query_handler(func=lambda call: call.data == constants.EXIT, state=MyStates.times)
def returnToDays(call: types.CallbackQuery):
    with bot.retrieve_data(call.from_user.id) as data:
        records = data[Context.RECORDS]
        daysRecords = utils.getRecordsWithDiffDays(records)
        bot.edit_message_text(text="Дни",
                              chat_id=call.from_user.id,
                              message_id=call.message.id,
                              reply_markup=keyboards.getDaysKeyMarkupByRecords(daysRecords))
    bot.set_state(call.from_user.id, MyStates.days)


@bot.callback_query_handler(func=recordsFullDateCallBack.filter().check, state=MyStates.times)
def checkTypeHandler(call: types.CallbackQuery):
    callback: dict = recordsFullDateCallBack.parse(call.data)
    date = machineStringToFullDate(callback["date"])

    with bot.retrieve_data(call.from_user.id) as data:
        data[Context.DATE] = date

    bot.set_state(call.from_user.id, MyStates.kinds_of_activity)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Выберите тип занятия\n" + fullDateToHumanString(date),
                          reply_markup=chooseTypeMarkup())


@bot.callback_query_handler(func=lambda call: call.data == constants.EXIT, state=MyStates.kinds_of_activity)
def returnToTimes(call: types.CallbackQuery):
    with bot.retrieve_data(call.from_user.id) as data:
        records = data[Context.RECORDS]
        daysRecords = utils.getRecordsByDay(records, data[Context.DATE])
        bot.edit_message_text(text="доступное время на " + utils.dateToHumanString(data[Context.DATE]),
                              chat_id=call.from_user.id,
                              message_id=call.message.id,
                              reply_markup=keyboards.getTimesMarkupWithRecords(daysRecords))
    bot.set_state(call.from_user.id, MyStates.times)


@bot.callback_query_handler(func=types_activity_callback.filter().check, state=MyStates.kinds_of_activity)
def addStudentHandler(call: types.CallbackQuery):
    callback: dict = types_activity_callback.parse(call.data)
    type = callback["type"]

    with bot.retrieve_data(call.from_user.id) as data:
        date = data[Context.DATE]
        records = data[Context.RECORDS]
        userName = data[Context.USER_NAME]

    record = findRecordByDate(records, date)
    cellForUser = record.getFreeNameCell()
    # check if another user get ahead of us (as we use old context from state machine
    if not googleSheet.addUser(userName, cellForUser, type):
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Это время было занято кем-то другим, попробуйте заново ')
        bot.delete_state(call.from_user.id)
        return

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text='Вы записаны на ' + utils.fullDateToHumanString(date),
                          reply_markup=cancelUserMarkup(cell=cellForUser, date=date))

    bot.delete_state(call.from_user.id)
    print(str(call.from_user.id) + "recordered")
    bot.send_message(constants.CREATOR_ID,
                     "На занятие " + utils.fullDateToHumanString(date) + " записался\n" + userName)

    googleSheet.addConnectedRecordMessages(date, call.message.id, call.from_user.id)


@bot.callback_query_handler(func=cancel_record_callback.filter().check)
def deleteUserHandler(call: types.CallbackQuery):
    callback: dict = cancel_record_callback.parse(call.data)

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Вы успешно отменили запись")

    googleSheet.deleteUser(callback["cell"])
    googleSheet.deleteUserFromRecords(userId=call.from_user.id, dateString=callback["date"])

