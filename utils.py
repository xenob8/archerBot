import datetime
import record
from time import sleep

import constants

from record import Record
from states import Context
import pause
from datetime import datetime




# def deleteRecord(dayIndex: int, timeIndex: int):
#     ids = googleSheet.getUsersIdByTime(dayIndex, timeIndex)
#     for id in ids:
#         print("DeleteRecprd with ", id)
#         msg = googleSheet.deleteRecord(id, dayIndex=dayIndex, timeIndex=timeIndex)
#         # change users message with record
#         bot.edit_message_text(text="Занятие перенесено", chat_id=id, message_id=msg)
#     return ids


def getFollowingRecord(records: list[Record], now: datetime):
    return min((record for record in records if record.date and record.date > now), key=lambda record: record.date)



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


def dateToHumanString(date: datetime):
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


def getAvalAdminRecords(records: list[Record]):
    avalRecords = []
    for record in records:
        if record.date and record.getCount() > 0 and record.date > datetime.now():
            avalRecords.append(record)
    return avalRecords

