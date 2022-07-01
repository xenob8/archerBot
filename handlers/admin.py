from telebot import types

from bot import getBot, getSheet
from constants import RETURN_DAYS_STATE, ADMINS
from keyboards import days_callback, getAdminTimesMarkUp, times_callback, getDaysKeyMarkup
from states import MyStates
from utils import deleteRecord

bot = getBot()
googleSheet = getSheet()


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


@bot.message_handler(commands=["delete"], chat_id=ADMINS)
def showDays(message: types.Message):
    days = googleSheet.getAvailableDays()
    bot.send_message(chat_id=message.chat.id, text="Выберите день для удаления", reply_markup=getDaysKeyMarkup(days))
    bot.set_state(message.chat.id, MyStates.admindays)
