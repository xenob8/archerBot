import telebot
from telebot import custom_filters
from telebot.storage import StateMemoryStorage
from states import MyStates
from database import GoogleSheet
from keyboards import *
import config
import filters


class BotSingletone:
    state_storage = StateMemoryStorage()
    bot = telebot.TeleBot(config.BOT_TOKEN, state_storage=state_storage)
    googleSheet = GoogleSheet()
    googleSheet.createFirstSheet("testArcher")
    googleSheet.createSheetById("testArcher", 312817610)
    googleSheet.createRecordsSheet("testArcher", 2027440591)


def getBot():
    return BotSingletone.bot


def getSheet():
    return BotSingletone.googleSheet
