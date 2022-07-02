from telebot import types

import constants
from bot import getBot, getSheet
from constants import RETURN_DAYS_STATE, ADMINS
from keyboards import days_callback, getAdminTimesMarkUp, times_callback, getDaysKeyMarkup
from states import MyStates, Context
from utils import deleteRecord

bot = getBot()
googleSheet = getSheet()


@bot.callback_query_handler(func=days_callback.filter().check, state=MyStates.admindays, chat_id_callback=ADMINS)
def showHoursHandler(call: types.CallbackQuery):
    callback_data: dict = days_callback.parse(call.data)
    dayIndex = callback_data["dayIndex"]
    dayString = callback_data["dayStr"]
    with bot.retrieve_data(call.from_user.id) as data:
        data[Context.ADMIN_DAY_INDEX] = dayIndex
        data[Context.ADMIN_DAY_STRING] = dayString
    times, numbers = googleSheet.getTimeAndCountListsByDay(dayIndex)
    print(times)
    print(numbers)
    timesMarkup = getAdminTimesMarkUp(times)

    timesMarkup.add(types.InlineKeyboardButton(text="Вернуться к расписанию",
                                               callback_data=RETURN_DAYS_STATE))

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Выберите время для удаления " + dayString, reply_markup=timesMarkup)

    bot.set_state(call.from_user.id, MyStates.admintimes)


@bot.callback_query_handler(func=times_callback.filter().check, state=MyStates.admintimes, chat_id_callback=ADMINS)
def deleteWork(call: types.CallbackQuery):
    print("deleteWork")
    callback: dict = times_callback.parse(call.data)

    with bot.retrieve_data(call.from_user.id) as data:
        timeIndex = callback["timeIndex"]
        timeStr = callback["timeStr"]

    ids = deleteRecord(data[Context.ADMIN_DAY_INDEX], timeIndex)

    for id in ids:
        bot.send_message(id, text="Внимаение, занятие " + data[
            Context.ADMIN_DAY_STRING] + " в " + timeStr + "было отменено")
    bot.delete_state(call.from_user.id)
    bot.reset_data(call.from_user.id)
    googleSheet.deleteUsersByTime(data[Context.ADMIN_DAY_INDEX], timeIndex)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Вы удалили занятие\n" + timeStr)


@bot.message_handler(commands=["delete"], chat_id=ADMINS)
def chooseDay(message: types.Message):
    days = googleSheet.getAvailableDays()
    bot.send_message(chat_id=message.chat.id, text="Выберите день для удаления", reply_markup=getDaysKeyMarkup(days))
    bot.set_state(message.chat.id, MyStates.admindays)


@bot.callback_query_handler(func=lambda call: call.data == RETURN_DAYS_STATE, state=MyStates.admintimes)
def returnToDays(call: types.CallbackQuery):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Доступные дни для удаления",
                          reply_markup=getDaysKeyMarkup(googleSheet.getAvailableDays()))
    bot.set_state(call.from_user.id, MyStates.admindays)
