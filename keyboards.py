from gspread import Cell
from telebot import types
from telebot.callback_data import CallbackData

import constants
import utils
from database import Record

MAX_STUDENTS_PER_TIME = 5

isShowDaysMarkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
recordExerciseButton = types.KeyboardButton("Записаться на занятие")
isShowDaysMarkup.add(recordExerciseButton)

returnFromTypeChoose = types.InlineKeyboardButton(text="выйти", callback_data=constants.EXIT)
deleteCommandButton = types.KeyboardButton("Отменить занятие")

recordsCallBack = CallbackData("dayFormatted", prefix="days")
recordsFullDateCallBack = CallbackData("date", prefix="times", sep="!")
types_activity_callback = CallbackData("type", prefix="sport")
cancel_record_callback = CallbackData("cell", prefix="cancel")


def getDaysKeyMarkupByRecords(dailyRecords: list[Record]):
    daysKeyMarkup = types.InlineKeyboardMarkup()
    keys = []
    for record in dailyRecords:
        keys.append(
            types.InlineKeyboardButton(text=utils.dateStringToHuman(record.date),
                                       callback_data=recordsCallBack.new(dayFormatted=record.dateCell.value)))
    daysKeyMarkup.add(*keys, row_width=2)
    daysKeyMarkup.add(types.InlineKeyboardButton(text="Выйти", callback_data=constants.EXIT))
    return daysKeyMarkup



# def getAdminDaysKeyMarkup(days):
#     daysKeyMarkup = types.InlineKeyboardMarkup()
#     keys = []
#     for dayIndex, day in enumerate(days):
#         if day.isAdmin():
#             keys.append(
#                 types.InlineKeyboardButton(text=day.dayText,
#                                            callback_data=days_callback.new(dayIndex=dayIndex, dayStr=day.dayText)))
#     daysKeyMarkup.add(*keys, row_width=2)
#     daysKeyMarkup.add(types.InlineKeyboardButton(text="Выйти", callback_data=constants.EXIT))
#     return daysKeyMarkup


# def getTimesMarkup(times):
#     timesMarkup = types.InlineKeyboardMarkup()
#
#     for timeIndex, time in enumerate(times):
#         if not time:
#             continue
#         timesMarkup.add(types.InlineKeyboardButton(
#             text=times[timeIndex],
#             callback_data=times_callback.new(timeIndex=timeIndex, timeStr=times[timeIndex])))
#
#     return timesMarkup


def getTimesMarkupWithRecords(oneDayRecords: list[Record]):
    timesMarkup = types.InlineKeyboardMarkup()

    for record in oneDayRecords:
        timesMarkup.add(types.InlineKeyboardButton(
            text=record.timeCell.value,
            callback_data=recordsFullDateCallBack.new(date=utils.fullDateToMachineString(record.date))))

    return timesMarkup


# def getAdminTimesMarkUp(times):
#     timesMarkup = types.InlineKeyboardMarkup()
#
#     for timeIndex, time in enumerate(times):
#         if not time:
#             continue
#         timesMarkup.add(types.InlineKeyboardButton(
#             text=time,
#             callback_data=times_callback.new(timeIndex=timeIndex, timeStr=time)))
#
#     return timesMarkup


def cancelRecordMarkup(personCell):
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="Отменить запись",
                                        callback_data=cancel_record_callback.new(cell=personCell))
    markup.add(button)
    return markup


def chooseTypeMarkup():
    markup = types.InlineKeyboardMarkup()
    buttonMk = types.InlineKeyboardButton(text="МК", callback_data=types_activity_callback.new("MK"))
    buttonSolo = types.InlineKeyboardButton(text="самостоятельное", callback_data=types_activity_callback.new("solo"))
    buttonEduc = types.InlineKeyboardButton(text="обучение", callback_data=types_activity_callback.new("educ"))
    markup.add(buttonMk, buttonSolo, buttonEduc)
    markup.add(returnFromTypeChoose)
    return markup


def adminDefaultMarkup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(recordExerciseButton)
    markup.add(deleteCommandButton)
    return markup
