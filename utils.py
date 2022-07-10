import datetime
from time import sleep

from database import FormattedDay
from loader import bot, googleSheet
from states import Context
import pause
from datetime import datetime


def getAvailableDays(userId):
    now = datetime.now()
    days = googleSheet.getAllDays()
    formatDays = googleSheet.getFormattedDays()
    for formatDay, day in zip(formatDays, days):
        if formatDay:
            if formatDay.dayDate.day < now.day:
                day.dayText = ""
                continue
            for timeIndex, timeDate in formatDay.datetimes.items():
                if timeDate < now:
                    day.times[timeIndex] = ""


    # if formatDay.
    # for timeIndex, time in formatDay.datetimes.items()
    #

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


def deleteRecord(dayIndex: int, timeIndex: int):
    ids = googleSheet.getUsersIdByTime(dayIndex, timeIndex)
    for id in ids:
        print("DeleteRecprd with ", id)
        msg = googleSheet.deleteRecord(id, dayIndex=dayIndex, timeIndex=timeIndex)
        # change users message with record
        bot.edit_message_text(text="Занятие перенесено", chat_id=id, message_id=msg)
    return ids


def deleteExpiredRecords():
    while True:
        now = datetime.now()
        days: list[FormattedDay] = googleSheet.getFormattedDays()
        dayIndex, timeIndex = FormattedDay.getMinDay(now, days)
        print("closest day in table:", dayIndex, timeIndex)
        if dayIndex != None:
            day = days[dayIndex]
            recordDate = day.datetimes[timeIndex]
            if (recordDate - now).seconds < 20: #//11*60:
                print("Отлично встали на паузу до", recordDate)
                pause.until(recordDate)
                print("Встали с паузы")
                ids = googleSheet.getUsersIdByTime(dayIndex, timeIndex)
                for id in ids:
                    msg = googleSheet.deleteRecord(id, dayIndex, timeIndex)
                    bot.edit_message_text(text="Время занятия истекло " + str(recordDate.strftime("%A %#d %B")),
                                          chat_id=id,
                                          message_id=msg)

        sleep(10)
