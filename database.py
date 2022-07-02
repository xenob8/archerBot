import itertools

from oauth2client.service_account import ServiceAccountCredentials
import gspread
from gspread import Cell
import numpy as np


class GoogleSheet:
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("testsheets-347919-bd50bf0daaae.json", scope)
    client = gspread.authorize(creds)
    sheet = []
    sheetId = []
    MAX_TIMES = 10
    types = {
        "MK": "МК",
        "solo": "Самостоятельное",
        "educ": "Обучение",
    }

    def createFirstSheet(self, sheetName):
        self.sheet = self.client.open(sheetName).sheet1
        return self.sheet

    def createSheetById(self, sheetName, id):
        self.sheetId = self.client.open(sheetName).get_worksheet_by_id(id)
        return self.sheetId

    def createRecordsSheet(self, sheetName, id):
        self.sheetRecord = self.client.open(sheetName).get_worksheet_by_id(id)
        return self.sheetId

    def getAvailableDays(self):
        list = self.sheet.batch_get(["day_0", "day_1", "day_2", "day_3", "day_4", "day_5", "day_6"])
        days = []
        for day in list:
            if day:
                days.append(day[0][0])
            else:
                days.append(None)
        return days

    def getTimeAndCountListsByDay(self, dayIndex):
        list = self.sheet.batch_get(["times" + dayIndex, "numbers" + dayIndex])
        times = np.array(list[0]).flatten()[0::2]
        numbers = np.array(list[1]).flatten()[0::2]
        return times, numbers

    def addStudent(self, type, dayIndex, timeIndex, userId):
        names_cells = self.sheet.range("names" + dayIndex)[int(timeIndex) * 2::self.MAX_TIMES]
        print(names_cells)
        name = self.getUserNameById(userId)
        for name_cell in names_cells:
            if name_cell.value == name:
                return None, "Вы уже записаны сюда"
            if not name_cell.value:
                self.sheet.update_cells([
                    gspread.cell.Cell(name_cell.row, name_cell.col, name),
                    gspread.cell.Cell(name_cell.row, name_cell.col + 1, self.types[type])
                ])

                return name_cell.address, name
        return None, None

    def getUserIdByName(self, name) -> int:
        nameCell: gspread.Cell = self.sheetId.find(name)
        id = self.sheetId.cell(nameCell.row, nameCell.col - 1).value
        return int(id)

    def getUsersIdByTime(self, dayIndex, timeIndex) -> list:
        names_cells = self.sheet.range("names" + dayIndex)[int(timeIndex) * 2::self.MAX_TIMES]
        print(names_cells)
        ids = []
        for name_cell in names_cells:
            name = name_cell.value
            if not name:
                continue
            else:
                ids.append(self.getUserIdByName(name))
        return ids

    def deleteUsersByTime(self, dayIndex, timeIndex):
        names_cells: list[Cell] = self.sheet.range("names" + dayIndex)[int(timeIndex) * 2::self.MAX_TIMES]
        types_cells = []
        for cell in names_cells:
            cell.value = ""
            types_cells.append(Cell(cell.row, cell.col + 1, ""))
        self.sheet.update_cells(names_cells + types_cells)

    def getUserNameById(self, id):
        idCell: gspread.Cell = self.sheetId.find(str(id))
        userNameCell = self.sheetId.range(idCell.row, idCell.col + 1)
        return userNameCell[0].value

    def deleteUser(self, cell):
        row, col = gspread.utils.a1_to_rowcol(cell)
        self.sheet.update_cells([
            gspread.cell.Cell(row, col, ""),
            gspread.cell.Cell(row, col + 1, ""),
        ])

    def registerUser(self, name, lastName, userId):
        idCell = self.sheetId.find(str(userId))
        if not idCell:
            self.sheetId.append_row([userId, name, lastName])
        else:
            self.sheetId.update_cells([gspread.cell.Cell(idCell.row, idCell.col + 1, name + " " + lastName)])

    def addRecord(self, userId, dayIndex, timeIndex, messageId):
        self.sheetRecord.append_row([userId, dayIndex, timeIndex, messageId])

    def deleteRecord(self, id, dayIndex, timeIndex):
        cells: list[Cell] = self.sheetRecord.findall(str(id), in_column=1)
        if cells:
            row = cells[0].row
            leng = len(cells)
            # wtf = self.sheetRecord.range(first_row=row, first_col=1, last_row=row + leng - 1, last_col=4)
            wtf: list[Cell] = self.sheetRecord.range(row, 2, row + leng - 1, 4)
            dayIndexes = wtf[0::3]
            timeIndexes = wtf[1::3]
            messId = wtf[2::3]
            for i, (day, time, mess) in enumerate(zip(dayIndexes, timeIndexes, messId)):
                print(day.value, time.value)
                if day.value == str(dayIndex) and time.value == str(timeIndex):
                    self.sheetRecord.delete_row(row + i)
                    return mess.value

    def deleteRecordByMessageId(self, messageId):
        messCell: Cell = self.sheetRecord.find(str(messageId), in_column=4)
        if messCell:
            self.sheetRecord.delete_row(messCell.row)
