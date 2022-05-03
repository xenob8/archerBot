from telebot import types

MAX_STUDENTS_PER_TIME = 5

def getDaysKeyMarkup(days):
    daysKeyMarkup = types.InlineKeyboardMarkup()
    keys = []
    for dayIndex, day in enumerate(days):
        if day:
            keys.append(types.InlineKeyboardButton(text=day, callback_data="day" + str(dayIndex) + day))
    daysKeyMarkup.add(*keys, row_width=2)
    return daysKeyMarkup

def getTimesMarkup(dayIndex, times, numbers):
    timesMarkup = types.InlineKeyboardMarkup()

    for timeIndex in range(len(times)):
        if not times[timeIndex]:
            continue
        if int(numbers[timeIndex]) < MAX_STUDENTS_PER_TIME:
            timesMarkup.add(types.InlineKeyboardButton(
                text=times[timeIndex],
                callback_data="ex" + dayIndex + str(timeIndex) + times[timeIndex]))

    return timesMarkup

def cancelRecordMarkup(personCell):
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="Отменить запись", callback_data='using' + personCell)
    markup.add(button)
    return markup