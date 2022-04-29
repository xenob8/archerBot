import telebot
from telebot import types
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import numpy
from gspread import utils

from telebot import custom_filters
from telebot.handler_backends import State, StatesGroup #States

# States storage
from telebot.storage import StateMemoryStorage

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("testsheets-347919-bd50bf0daaae.json", scope)

client = gspread.authorize(creds)
sheet = client.open("testArcher").sheet1
sheetId = client.open("testArcher").get_worksheet_by_id(312817610)

state_storage = StateMemoryStorage()
bot = telebot.TeleBot('5317874926:AAHaK_cQSRpMofm83nSYSubhSUptaLSRQpQ', state_storage=state_storage)
TIMES = ["12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]

recordExerciseMarkup = types.ReplyKeyboardMarkup()
recordExerciseButton = types.KeyboardButton("Записаться на занятие для новичков")
recordExerciseMarkup.add(recordExerciseButton)

class MyStates(StatesGroup):
    # Just name variables differently
    name = State() # creating instances of State class is enough from now
    surname = State()



# Команда start
@bot.message_handler(commands=["start"])
def start(message):
    firstName = message.from_user.first_name
    lastName = message.from_user.last_name
    bot.send_message(message.chat.id, 'Привет, ' + ' '.join(filter(None, [firstName, lastName])))
    bot.send_message(message.chat.id, "Начинаем регистрацию")

    bot.set_state(message.from_user.id, MyStates.name, message.chat.id)
    bot.send_message(message.chat.id, "Введите ваше имя")


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
    bot.send_message(message.chat.id, "Регистрация пройдена", reply_markup=recordExerciseMarkup)


    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['surname'] = message.text

    idCell = sheetId.find(str(message.from_user.id))
    if not idCell:
        sheetId.append_row([message.from_user.id, data['name'], data['surname']])
    else:
        sheetId.update_cells([gspread.cell.Cell(idCell.row, idCell.col+1, data['name']), gspread.cell.Cell(idCell.row, idCell.col+2, data['surname'])])

    bot.delete_state(message.from_user.id, message.chat.id)



@bot.message_handler(content_types=['text'])
def messageHandler(message):



    if message.text == "Записаться на занятие для новичков":
        list = sheet.batch_get(["day_1", "day_2", "day_3", "numbers1", "numbers2", "numbers3"])
        global days
        days = numpy.array(list[0:3]).flatten()

        numbers = []
        for i in range(3,6):
           numbers.append(numpy.array(list[i]).flatten().tolist())



        dayKeyBoards = []

        for day in days:
         dayKeyBoards.append(types.InlineKeyboardButton(text=day, callback_data="111"))

        markup = types.InlineKeyboardMarkup()
        markup.add(*dayKeyBoards)

        timeDisplayBoards = []


        for time in range(len(TIMES)):
            timeDisplayBoards = []
            for day in range(len(days)):
                if int(numbers[day][time]) < 3:
                    timeDisplayBoards.append(types.InlineKeyboardButton(text=TIMES[time], callback_data="good"+str(day+1)+str(time)))
                else:
                    timeDisplayBoards.append(types.InlineKeyboardButton(text="---", callback_data="bad"))
            markup.add(*timeDisplayBoards)


        bot.send_message(message.chat.id, "Когда хотите записаться", reply_markup=markup)





@bot.callback_query_handler(func=lambda call: True)
def queryHandler(call):
    if call.data.find("good") != -1:
        day = call.data[-2]
        time = int(call.data[-1])

        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text="Отменить занятие", callback_data='inUse' + day + str(time))
        markup.add(button)


        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Вы записаны на ' + TIMES[time] + " " + days[int(day)-1],
                              reply_markup=markup)

        names_cells = sheet.range("names"+day)[time::len(TIMES)] #Search by named range


        for name_cell in names_cells:
            if not name_cell.value:
                idCell = sheetId.find(str(call.from_user.id))
                userNameCell = sheetId.range(idCell.row, idCell.col+1, idCell.row, idCell.col+2)
                sheet.update_acell(name_cell.address, userNameCell[0].value + userNameCell[1].value)
                break



    if call.data.find("inUse") != -1:


        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="Вы успешно отменили запись")

        idCell = sheetId.find(str(call.from_user.id))
        userData = sheetId.range(idCell.row, idCell.col + 1, idCell.row, idCell.col + 2)
        deleteUserCell = sheet.find(userData[0].value + userData[1].value)
        if not deleteUserCell:
            return
        sheet.update_acell(deleteUserCell.address, "")



bot.add_custom_filter(custom_filters.StateFilter(bot))
# Запускаем бота
bot.polling(none_stop=True, interval=0)
