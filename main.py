from telebot import custom_filters
import filters
from bot import getBot, getSheet
import handlers

bot = getBot()

googleSheet = getSheet()

bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.TextMatchFilter())
bot.add_custom_filter(custom_filters.ChatFilter())
bot.add_custom_filter(filters.ChatFilterCallback())

# Запускаем бота
bot.polling(none_stop=True, interval=0)
