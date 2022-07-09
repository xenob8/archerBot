from threading import Thread
from time import sleep

import telebot
from telebot import custom_filters
import filters
from loader import bot, googleSheet
from handlers import *






bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.TextMatchFilter())
bot.add_custom_filter(custom_filters.ChatFilter())
bot.add_custom_filter(filters.ChatFilterCallback())

thread = Thread(target=utils.deleteExpiredRecords())
thread.start()

bot.polling(none_stop=True, interval=0)
