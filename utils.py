import datetime
from time import sleep

from database import FormattedDay
from loader import bot, googleSheet
from states import Context


def getAvailableDays(userId):
    days = googleSheet.getAllDays()
    map = googleSheet.getUserDaysAndTimesById(userId)

    for i, day in enumerate(days):
        day.getValidTimes()
        if map.get(i):
            day.killSelfRecords(map[i])

    return days

def getAdminTimesByDayIndex(dayIndex):
    day = googleSheet.getAllDays()[dayIndex]
    for i, (time, count) in enumerate(zip(day.times, day.numbers)):
        if int(count) == 0:
            day.times[i] = ""
    return day





def deleteRecord(dayIndex:int, timeIndex:int):
    ids = googleSheet.getUsersIdByTime(dayIndex, timeIndex)
    for id in ids:
        print("DeleteRecprd with ", id)
        msg = googleSheet.deleteRecord(id, dayIndex=dayIndex, timeIndex=timeIndex)
        #change users message with record
        bot.edit_message_text(text="Занятие перенесено", chat_id=id, message_id=msg)
    return ids

def deleteExpiredRecords():
    oldTime = datetime.datetime(1899, 12, 30)
    while True:
        sleep(60)
        now = datetime.datetime.now()
        days: list[FormattedDay] = googleSheet.getFormattedDays()
        for dayIndex, day in enumerate(days):
            if day:
                for timeIndex, time in enumerate(day.times):
                    if time:
                        dayTime = oldTime + datetime.timedelta(days=day.dayText + time)
                        if now > dayTime:
                            ids = googleSheet.getUsersIdByTime(dayIndex, timeIndex)
                            for id in ids:
                                msg = googleSheet.deleteRecord(id, dayIndex, timeIndex)
                                googleSheet.deleteTime(dayIndex, timeIndex)
                                bot.edit_message_text(text="Время занятия истекло " + str(dayTime), chat_id=id,
                                                      message_id=msg)

