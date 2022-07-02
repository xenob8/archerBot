from telebot import types
from telebot.callback_data import CallbackData

import constants

MAX_STUDENTS_PER_TIME = 5

isShowDaysMarkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
recordExerciseButton = types.KeyboardButton("Записаться на занятие")
isShowDaysMarkup.add(recordExerciseButton)

days_callback = CallbackData("dayIndex", "dayStr", prefix="days")
times_callback = CallbackData("timeIndex", "timeStr", prefix="times", sep="!")
types_activity_callback = CallbackData("type", prefix="sport")
cancel_record_callback = CallbackData("cell", prefix="cancel")


def getDaysKeyMarkup(days):
    daysKeyMarkup = types.InlineKeyboardMarkup()
    keys = []
    for dayIndex, day in enumerate(days):
        if day:
            keys.append(
                types.InlineKeyboardButton(text=day, callback_data=days_callback.new(dayIndex=dayIndex, dayStr=day)))
    daysKeyMarkup.add(*keys, row_width=2)
    daysKeyMarkup.add(types.InlineKeyboardButton(text="Выйти", callback_data=constants.EXIT))
    return daysKeyMarkup


def getTimesMarkup(dayIndex, times, numbers):
    timesMarkup = types.InlineKeyboardMarkup()

    for timeIndex in range(len(times)):
        if not times[timeIndex]:
            continue
        if int(numbers[timeIndex]) < MAX_STUDENTS_PER_TIME:
            timesMarkup.add(types.InlineKeyboardButton(
                text=times[timeIndex],
                callback_data=times_callback.new(timeIndex=timeIndex, timeStr=times[timeIndex])))

    return timesMarkup


def getAdminTimesMarkUp(times):
    timesMarkup = types.InlineKeyboardMarkup()

    for timeIndex in range(len(times)):
        if not times[timeIndex]:
            continue
        timesMarkup.add(types.InlineKeyboardButton(
            text=times[timeIndex],
            callback_data=times_callback.new(timeIndex=timeIndex, timeStr=times[timeIndex])))

    return timesMarkup


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
    return markup
