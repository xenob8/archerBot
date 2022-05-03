import itertools

from oauth2client.service_account import ServiceAccountCredentials
import gspread
import numpy as np


class GoogleSheet:
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("testsheets-347919-bd50bf0daaae.json", scope)
    client = gspread.authorize(creds)
    sheet = []
    sheetId = []
    MAX_TIMES = 10


    def createFirstSheet(self, sheetName):
        self.sheet = self.client.open(sheetName).sheet1
        return self.sheet

    def createSheetById(self, sheetName, id):
        self.sheetId = self.client.open(sheetName).get_worksheet_by_id(id)
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
        times = np.array(list[0]).flatten()
        numbers = np.array(list[1]).flatten()
        return times, numbers

    def addStudent(self, dayIndex, timeIndex, userId):
        names_cells = self.sheet.range("names" + dayIndex)[int(timeIndex)::self.MAX_TIMES]
        for name_cell in names_cells:
            if not name_cell.value:
                name = self.getUserNameById(userId)
                self.sheet.update_acell(name_cell.address, name)
                return name_cell.address, name
        return None, None


    def getUserNameById(self, id):
        idCell = self.sheetId.find(str(id))
        userNameCell = self.sheetId.range(idCell.row, idCell.col + 1, idCell.row, idCell.col + 2)
        return userNameCell[0].value + " " + userNameCell[1].value

    def deleteUser(self, cell):
        self.sheet.update_acell(cell, "")

    def registerUser(self, name, lastName, userId):
        idCell = self.sheetId.find(str(userId))
        if not idCell:
            self.sheetId.append_row([userId, name, lastName])
        else:
            self.sheetId.update_cells([gspread.cell.Cell(idCell.row, idCell.col + 1, name),
                                  gspread.cell.Cell(idCell.row, idCell.col + 2, lastName)])
