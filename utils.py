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

def foo():
    days = googleSheet.getAllDays()
    map = googleSheet.getUserDaysAndTimesById(480316781)
    # for key, val in map.items():
    #     print("mapkey:", key)
    for i, day in enumerate(days):
        day.getValidTimes()
        if map.get(str(i)):
            day.killSelfRecords(map[str(i)])

