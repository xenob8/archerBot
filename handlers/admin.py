from telebot import types

import keyboards
import utils
from loader import bot, googleSheet
from constants import RETURN_DAYS_STATE, ADMINS
from keyboards import *
from states import MyStates, Context

@bot.message_handler(state=[MyStates.admindays, MyStates.admintimes, MyStates.times, MyStates.days, MyStates.kinds_of_activity])
def trash(message: types.Message):
    bot.send_message(message.from_user.id, text="Завершите предыдущее действие")

@bot.message_handler(text="Отменить занятие", chat_id=ADMINS)
def showDay(message: types.Message):
    records = googleSheet.getAllRecords()
    avalRecords = utils.getAvalAdminRecords(records)
    dayRecords = utils.getRecordsWithDiffDays(avalRecords)
    bot.send_message(chat_id=message.chat.id, text="Выберите день для удаления",
                     reply_markup=getDaysKeyMarkupByRecords(dayRecords))
    bot.set_state(message.from_user.id, MyStates.admindays)
    with bot.retrieve_data(message.from_user.id) as data:
        data[Context.RECORDS] = avalRecords


@bot.callback_query_handler(func=lambda call: call.data == constants.EXIT, state=MyStates.admindays,
                            chat_id_callback=ADMINS)
def exitToMainMenu(call: types.CallbackQuery):
    bot.delete_state(call.from_user.id)
    bot.delete_message(chat_id=call.from_user.id, message_id=call.message.id)


@bot.callback_query_handler(func=recordsCallBack.filter().check, state=MyStates.admindays, chat_id_callback=ADMINS)
def showHoursHandler(call: types.CallbackQuery):
    callback_data: dict = recordsCallBack.parse(call.data)
    date = utils.dayStringToDatetime(callback_data["dayFormatted"])
    with bot.retrieve_data(call.from_user.id) as data:
        data[Context.DATE] = date
        avalRecords = data[Context.RECORDS]

    dayRecords = utils.getRecordsByDay(avalRecords, date)

    timesMarkup = getTimesMarkupWithRecords(dayRecords)

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Выберите время для удаления " + utils.dateToHumanString(date), reply_markup=timesMarkup)

    bot.set_state(call.from_user.id, MyStates.admintimes)


@bot.callback_query_handler(func=lambda call: call.data == constants.EXIT, state=MyStates.admintimes,
                            chat_id_callback=ADMINS)
def returnToDays(call: types.CallbackQuery):
    with bot.retrieve_data(call.from_user.id) as data:
        avalRecords = data[Context.RECORDS]
        dayRecords = utils.getRecordsWithDiffDays(avalRecords)

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id, text="Время для удаления",
                          reply_markup=getDaysKeyMarkupByRecords(dayRecords))

    bot.set_state(user_id=call.from_user.id, state=MyStates.admindays)


@bot.callback_query_handler(func=recordsFullDateCallBack.filter().check, state=MyStates.admintimes,
                            chat_id_callback=ADMINS)
def deleteWork(call: types.CallbackQuery):
    print("deleteWork")
    callback: dict = recordsFullDateCallBack.parse(call.data)

    date = utils.machineStringToFullDate(callback["date"])
    with bot.retrieve_data(call.from_user.id) as data:
        records = data[Context.RECORDS]

    record = utils.findRecordByDate(records, date)
    msgList = googleSheet.getMsgIdAndUserIdByRecordAndDelete(date)

    for (msgId, userId) in msgList:
        print("msg id", msgId, "userid:", userId)
        bot.send_message(userId, text="Внимаение, занятие " + utils.fullDateToHumanString(date) + "было отменено")
        bot.edit_message_text(text=utils.fullDateToHumanString(date) + "отменено администратором", chat_id=userId,
                              message_id=msgId)
    bot.delete_state(call.from_user.id)
    bot.reset_data(call.from_user.id)
    googleSheet.deleteRecord(record)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Вы удалили занятие\n" + utils.fullDateToHumanString(date))
