import datetime
from time import sleep

import constants
from loader import bot, googleSheet
from record import Record
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


# def deleteExpiredRecords():
#     while True:
#         now = datetime.now()
#         days: list[FormattedDay] = googleSheet.getFormattedDays()
#         dayIndex, timeIndex = FormattedDay.getMinDay(now, days)
#         print("closest day in table:", dayIndex, timeIndex)
#         if dayIndex != None:
#             day = days[dayIndex]
#             recordDate = day.datetimes[timeIndex]
#             if (recordDate - now).seconds < 20:  # //11*60:
#                 print("Отлично встали на паузу до", recordDate)
#                 pause.until(recordDate)
#                 print("Встали с паузы")
#                 ids = googleSheet.getUsersIdByTime(dayIndex, timeIndex)
#                 for id in ids:
#                     msg = googleSheet.deleteRecord(id, dayIndex, timeIndex)
#                     bot.edit_message_text(text="Время занятия истекло " + str(recordDate.strftime("%A %#d %B")),
#                                           chat_id=id,
#                                           message_id=msg)
#
#         sleep(10)


def getAvaliableRecords(records: list[Record], userName):
    avalRecords = []
    nowDate = datetime.now()
    for record in records:
        print("try to aval records:", record.date)
        if record.timeCell.value \
                and record.date \
                and record.date > nowDate \
                and record.getCount() < constants.MAX_USERS_AT_RECORD \
                and userName not in [nameCell.value for nameCell in record.nameCells if nameCell.value]:
            avalRecords.append(record)
            print("aval records:", record.date)

    return avalRecords


def getRecordsWithDiffDays(records: list[Record]):
    diffRecords = []
    for record in records:
        if record.date and record.date.day not in [diffRec.date.day for diffRec in diffRecords]:
            diffRecords.append(record)
    return diffRecords


def dayStringToDatetime(dayString):
    return datetime.strptime(dayString, "%d.%m.%Y")


def fullDateToMachineString(fullDate: datetime):
    return fullDate.strftime("%d.%m.%Y %H:%M")


def fullDateToHumanString(fullDate: datetime):
    return fullDate.strftime("%B %#d, %A в %H:%M")


def dateStringToHuman(date: datetime):
    return date.strftime("%B %#d, %A")


def machineStringToFullDate(string):
    return datetime.strptime(string, "%d.%m.%Y %H:%M")


def getRecordsByDay(records: list[Record], day: datetime):
    recordsByDay = []
    for record in records:
        if record.date and record.date.day == day.day and record.date.month == day.month:
            recordsByDay.append(record)
    return recordsByDay


def findRecordByDate(records: list[Record], date: datetime) -> Record:
    return next((record for record in records if record.date == date), None)


def getShowDaysHandlerRecords(userName):
    records = googleSheet.getAllRecords()
    records = getAvaliableRecords(records, userName)
    records = getRecordsWithDiffDays(records)
    return records


def getShowHoursHandlerRecords(day: datetime, userName):
    records = googleSheet.getAllRecords()
    records = getAvaliableRecords(records, userName)
    records = getRecordsByDay(records, day)
    return records


def findCellForUser(date: datetime):
    records = googleSheet.getAllRecords()
    record = findRecordByDate(records, date)
    cellForUser = record.getFreeNameCell()
    return cellForUser
