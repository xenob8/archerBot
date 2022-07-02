import telebot
from telebot import custom_filters
import filters
from bot import getBot, getSheet
import handlers
from constants import CREATOR_ID

bot = getBot()

googleSheet = getSheet()

bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.TextMatchFilter())
bot.add_custom_filter(custom_filters.ChatFilter())
bot.add_custom_filter(filters.ChatFilterCallback())

# googleSheet.deleteRecord(5,2,3)
googleSheet.deleteRecord(5, 3, 3)

bot.polling(none_stop=True, interval=0)
