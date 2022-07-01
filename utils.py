from bot import getBot, getSheet

bot = getBot()
googleSheet = getSheet()

def deleteRecord(dayIndex, timeIndex):
    ids = googleSheet.getUsersIdByTime(dayIndex, timeIndex)
    for id in ids:
        print(id)
        with bot.retrieve_data(id) as data:
            mess = data["messageId"]
            cell = data["cell"]

        bot.reset_data(id)
        bot.delete_state(id)
        googleSheet.deleteUser(cell)
        bot.send_message(id, text="ur acti canceled")
        bot.edit_message_text(chat_id=id, message_id=mess, text="Canceled")