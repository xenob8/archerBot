import locale
from threading import Thread
from time import sleep

import telebot
from telebot import custom_filters
import filters
from loader import bot, googleSheet
from handlers import *



def foo():
    while True:
        print("I am in thread")
        sleep(100)


bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.TextMatchFilter())
bot.add_custom_filter(custom_filters.ChatFilter())
bot.add_custom_filter(filters.ChatFilterCallback())
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

# thread = Thread(target=utils.deleteExpiredRecords)

# thread.start()
# print("dffdf")

bot.polling(none_stop=True, interval=0)
