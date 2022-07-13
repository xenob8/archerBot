import locale
from threading import Thread
from time import sleep

import telebot
from telebot import custom_filters
import filters
from loader import bot, googleSheet
from handlers import *

def deleteExpiredRecords():
    while True:
        now = datetime.now()
        records = googleSheet.getAllRecords()
        record = getFollowingRecord(records, now)

        print("closest day in table:", record.date)
        if record != None:
            if (record.date - now).seconds < 20:  # //11*60:
                print("Отлично встали на паузу до", record.date())
                pause.until(record.date())
                print("Встали с паузы")
                # delete guy and send message to him

        sleep(10)



bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.TextMatchFilter())
bot.add_custom_filter(custom_filters.ChatFilter())
bot.add_custom_filter(filters.ChatFilterCallback())
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

thread = Thread(target=deleteExpiredRecords)

thread.start()
# print("dffdf")

bot.polling(none_stop=True, interval=0, skip_pending=True)


