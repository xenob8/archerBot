import telebot
from telebot import custom_filters
from telebot.handler_backends import State, StatesGroup  # States

# States storage
from telebot.storage import StateMemoryStorage
from database import GoogleSheet
from keyboards import *
import config



state_storage = StateMemoryStorage()
bot = telebot.TeleBot(config.BOT_TOKEN, state_storage=state_storage)

isShowDaysMarkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
recordExerciseButton = types.KeyboardButton("Записаться на занятие")
isShowDaysMarkup.add(recordExerciseButton)

#MY_CHAT_ID = 317800531


class MyStates(StatesGroup):
    # Just name variables differently
    name = State()  # creating instances of State class is enough from now
    surname = State()


# Команда start
@bot.message_handler(commands=["start"])
def start(message):
    firstName = message.from_user.first_name
    lastName = message.from_user.last_name
    bot.send_message(message.chat.id, 'Привет, ' + ' '.join(filter(None, [firstName, lastName])))
    bot.send_message(message.chat.id, "Начинаем регистрацию")

    bot.set_state(message.from_user.id, MyStates.name, message.chat.id)
    bot.send_message(message.chat.id, "Введите ваше имя(без фамилии)")


@bot.message_handler(state="*", commands=['cancel'])
def any_state(message):
    """
    Cancel state
    """
    bot.send_message(message.chat.id, "Your state was cancelled.")
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state=MyStates.name)
def name_get(message):
    """
    State 1. Will process when user's state is MyStates.name.
    """
    bot.send_message(message.chat.id, f'Введите фамилию')
    bot.set_state(message.from_user.id, MyStates.surname, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['name'] = message.text


@bot.message_handler(state=MyStates.surname)
def registationEnd(message):
    """
    State 2. Will process when user's state is MyStates.surname.
    """
    bot.send_message(message.chat.id, "Регистрация пройдена", reply_markup=isShowDaysMarkup)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['surname'] = message.text

    googleSheet.registerUser(data['name'], data['surname'], message.from_user.id)

    # idCell = sheetId.find(str(message.from_user.id))
    # if not idCell:
    #     sheetId.append_row([message.from_user.id, data['name'], data['surname']])
    # else:
    #     sheetId.update_cells([gspread.cell.Cell(idCell.row, idCell.col + 1, data['name']),
    #                           gspread.cell.Cell(idCell.row, idCell.col + 2, data['surname'])])

    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(content_types=['text'])
def showDays(message):
    if message.text == "Записаться на занятие":  # "Выберите день для записи":
        days = googleSheet.getAvailableDays()
        bot.send_message(message.chat.id, "Выберите день для записи", reply_markup=getDaysKeyMarkup(days))


@bot.callback_query_handler(func=lambda call: call.data.find("day") != -1)
def showHoursHandler(call):
    dayIndex = call.data[3]
    dayString = call.data[4:]
    times, numbers = googleSheet.getTimeAndCountListsByDay(dayIndex)
    print(times)
    print(numbers)

    timesMarkup = getTimesMarkup(dayIndex, times, numbers)

    timesMarkup.add(types.InlineKeyboardButton(text="Вернуться к расписанию",
                                               callback_data="return to timeTable"))

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Доступное время на" + dayString, reply_markup=timesMarkup)


@bot.callback_query_handler(func=lambda call: call.data.find("ct") != -1)
def checkTypeHandler(call):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Выберите тип занятия\n" + call.message.text[18:], reply_markup=chooseTypeMarkup(call.data))

@bot.callback_query_handler(func=lambda call: call.data.find("ex") != -1)
def addStudentHandler(call):
    # callback_data="ex" + dayIndex + str(timeIndex) + times[timeIndex]))
    # callback_data="exMk__" + dayIndex + str(timeIndex) + times[timeIndex]))
    type = call.data[2:6]
    dayIndex = call.data[6]
    timeIndex = call.data[7]
    timeValue = call.data[8:]
    print(timeIndex)

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text='Записываемся...')

    address, name = googleSheet.addStudent(type, dayIndex, timeIndex, call.from_user.id)

    if address:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Вы записаны на ' + timeValue + " " + call.message.text[21:],
                              reply_markup=cancelRecordMarkup(address))

        #bot.send_message(MY_CHAT_ID, "На занятие " + call.message.text[18:] + " в " + timeValue + " записался\n" + name)
    else:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Ошибка записи, попробуйте другое время\n' + name,
                              reply_markup=getDaysKeyMarkup(googleSheet.getAvailableDays()))


@bot.callback_query_handler(func=lambda call: call.data.find("using") != -1)
def deleteUserHandler(call):
    cell = call.data[5:]

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Вы успешно отменили запись")

    googleSheet.deleteUser(cell)


@bot.callback_query_handler(func=lambda call: True)
def queryHandler(call):
    if call.data == "return to timeTable":
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="Доступное время", reply_markup=getDaysKeyMarkup(googleSheet.getAvailableDays()))


googleSheet = GoogleSheet()
googleSheet.createFirstSheet("testArcher")
googleSheet.createSheetById("testArcher", 312817610)

bot.add_custom_filter(custom_filters.StateFilter(bot))
# Запускаем бота
bot.polling(none_stop=True, interval=0)
