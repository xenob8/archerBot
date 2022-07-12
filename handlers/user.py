from telebot import types

import constants
import utils
from loader import bot, googleSheet
from constants import RETURN_DAYS_STATE
from keyboards import *
from record import Record
from states import MyStates, Context
from utils import *


@bot.callback_query_handler(func=recordsCallBack.filter().check, state=MyStates.days)
def showHoursHandler(call: types.CallbackQuery):
    callback_data: dict = recordsCallBack.parse(call.data)
    dayStringFormat = callback_data["dayFormatted"]
    date = utils.dayStringToDatetime(dayStringFormat)


    records = utils.getShowHoursHandlerRecords(date, googleSheet.getUserNameById(call.from_user.id))

    timesMarkup = getTimesMarkupWithRecords(records)

    timesMarkup.add(types.InlineKeyboardButton(text="Вернуться к расписанию",
                                               callback_data=RETURN_DAYS_STATE))

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Доступное время на " + utils.dateStringToHuman(date), reply_markup=timesMarkup)

    bot.set_state(call.from_user.id, MyStates.times)


@bot.callback_query_handler(func=lambda call: call.data == RETURN_DAYS_STATE)
def returnToDays(call: types.CallbackQuery):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Доступное время",
                          reply_markup=getDaysKeyMarkupByRecords(
                              utils.getShowDaysHandlerRecords(googleSheet.getUserNameById(call.from_user.id))))
    bot.set_state(call.from_user.id, MyStates.days)


@bot.callback_query_handler(func=lambda call: call.data == constants.EXIT, state=[MyStates.days, MyStates.admindays, MyStates.kinds_of_activity])
def exit(call: types.CallbackQuery):
    bot.delete_message(chat_id=call.message.chat.id,
                       message_id=call.message.message_id)
    bot.delete_state(call.from_user.id)


@bot.message_handler(state=MyStates.days)
def showHoursHandler(call: types.CallbackQuery):
    bot.send_message(call.from_user.id, text="Выберите нужную кнопку")


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


@bot.message_handler(state=MyStates.times)
def checkTypeHandler(call: types.CallbackQuery):
    bot.send_message(call.from_user.id, text="Выберите нужную кнопку")


@bot.callback_query_handler(func=types_activity_callback.filter().check, state=MyStates.kinds_of_activity)
def addStudentHandler(call: types.CallbackQuery):
    callback: dict = types_activity_callback.parse(call.data)
    type = callback["type"]
    with bot.retrieve_data(call.from_user.id) as data:
        date = data[Context.DATE]
        userName = googleSheet.getUserNameById(call.from_user.id)
        cellForUser = utils.findCellForUser(date)
        googleSheet.addUser(userName, cellForUser, type)

        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Вы записаны на ' + utils.fullDateToHumanString(date),
                              reply_markup=cancelRecordMarkup(str(cellForUser.address)))

    bot.delete_state(call.from_user.id)
    print(str(call.from_user.id) + "recordered")
    bot.send_message(constants.CREATOR_ID,
                     "На занятие " + utils.fullDateToHumanString(date) + " записался\n" + userName)



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
    records = getShowDaysHandlerRecords(googleSheet.getUserNameById(message.from_user.id))

    bot.send_message(chat_id=message.chat.id, text="Выберите день для записи",
                     reply_markup=getDaysKeyMarkupByRecords(records))
    bot.set_state(message.chat.id, MyStates.days)
