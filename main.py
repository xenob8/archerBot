import telebot
from telebot import custom_filters
import filters
from loader import bot, googleSheet
from handlers import *




bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.TextMatchFilter())
bot.add_custom_filter(custom_filters.ChatFilter())
bot.add_custom_filter(filters.ChatFilterCallback())

@bot.message_handler(text="111")
def hi(mess):
    print("hi")

print("ues")

bot.polling(none_stop=True, interval=0)
