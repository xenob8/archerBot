from bot import getBot, getSheet
from states import Context

bot = getBot()
googleSheet = getSheet()


def deleteRecord(dayIndex, timeIndex):
    ids = googleSheet.getUsersIdByTime(dayIndex, timeIndex)
    for id in ids:
        print("DeleteRecprd with ", id)
        msg = googleSheet.deleteRecord(id, dayIndex=dayIndex, timeIndex=timeIndex)
        #change users message with record
        bot.edit_message_text(text="Занятие перенесено", chat_id=id, message_id=msg)
    return ids

