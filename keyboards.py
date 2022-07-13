from gspread import Cell
from telebot import types
from telebot.callback_data import CallbackData

import constants
import utils
from database import Record

isShowDaysMarkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
recordExerciseButton = types.KeyboardButton("Записаться на занятие")
isShowDaysMarkup.add(recordExerciseButton)

returnBackButton = types.InlineKeyboardButton(text="назад", callback_data=constants.EXIT)
exitButton = types.InlineKeyboardButton(text="выйти", callback_data=constants.EXIT)
deleteCommandButton = types.KeyboardButton("Отменить занятие")

recordsCallBack = CallbackData("dayFormatted", prefix="days")
recordsFullDateCallBack = CallbackData("date", prefix="times", sep="!")
types_activity_callback = CallbackData("type", prefix="sport")
cancel_record_callback = CallbackData("cell", "date", prefix="cancel", sep="!")


def adminDefaultMarkup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(recordExerciseButton)
    markup.add(deleteCommandButton)
    return markup


def getDaysKeyMarkupByRecords(dailyRecords: list[Record]):
    daysKeyMarkup = types.InlineKeyboardMarkup()
    keys = []
    for record in dailyRecords:
        keys.append(
            types.InlineKeyboardButton(text=utils.dateToHumanString(record.date),
                                       callback_data=recordsCallBack.new(dayFormatted=record.dateCell.value)))
    daysKeyMarkup.add(*keys, row_width=2)
    daysKeyMarkup.add(exitButton)
    return daysKeyMarkup


def getTimesMarkupWithRecords(oneDayRecords: list[Record]):
    timesMarkup = types.InlineKeyboardMarkup()

    for record in oneDayRecords:
        timesMarkup.add(types.InlineKeyboardButton(
            text=record.timeCell.value,
            callback_data=recordsFullDateCallBack.new(date=utils.fullDateToMachineString(record.date))))

    timesMarkup.add(returnBackButton)

    return timesMarkup


def chooseTypeMarkup():
    markup = types.InlineKeyboardMarkup()
    buttonMk = types.InlineKeyboardButton(text="МК", callback_data=types_activity_callback.new("MK"))
    buttonSolo = types.InlineKeyboardButton(text="самостоятельное", callback_data=types_activity_callback.new("solo"))
    buttonEduc = types.InlineKeyboardButton(text="обучение", callback_data=types_activity_callback.new("educ"))
    markup.add(buttonMk, buttonSolo, buttonEduc)
    markup.add(returnBackButton)
    return markup


def cancelUserMarkup(cell: Cell, date):
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="Отменить запись",
                                        callback_data=cancel_record_callback.new(cell=cell.address,
                                                                                 date=utils.fullDateToMachineString(
                                                                                     date)))
    markup.add(button)
    return markup
