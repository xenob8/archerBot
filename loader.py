import telebot
from telebot.storage import StateMemoryStorage
from database import GoogleSheet
import config



state_storage = StateMemoryStorage()
bot = telebot.TeleBot(config.BOT_TOKEN, state_storage=state_storage)

bot.set_my_commands(
    commands=[
        telebot.types.BotCommand("start", "Начать"),
        telebot.types.BotCommand("edit", "Изменить данные профиля")
    ],
    # scope=telebot.types.BotCommandScopeChat(12345678)  # use for personal command for users
    # scope=telebot.types.BotCommandScopeAllPrivateChats()  # use for all private chats
)

googleSheet = GoogleSheet()
googleSheet.createFirstSheet("testArcher")
googleSheet.createSheetById("testArcher", 312817610)
googleSheet.createRecordsSheet("testArcher", 2027440591)
