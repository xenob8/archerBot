import builtins
from datetime import datetime, timedelta
import itertools
import re

from oauth2client.service_account import ServiceAccountCredentials
import gspread
from gspread import Cell
import numpy as np
from gspread.utils import ValueRenderOption, ValueInputOption
# from utils import fullDateToMachineString
import config
import constants
import utils
from record import Record
from utils import fullDateToMachineString


class GoogleSheet:
    MAX_TIMES = 10
    types = {
        "MK": "МК",
        "solo": "Самостоятельное",
        "educ": "Обучение",
    }
    MAX_DAYS = 7
    MESSAGE_ID_COL = 4

    def __init__(self):
        creds = ServiceAccountCredentials.from_json_keyfile_name("testsheets-347919-bd50bf0daaae.json", config.scope)
        self.client = gspread.authorize(creds)

    def addUser(self, username, cell: Cell, type):
        if self.sheet.cell(cell.row, cell.col).value:
            return False
        self.sheet.update_cells(
            [Cell(row=cell.row, col=cell.col, value=username), Cell(row=cell.row, col=cell.col + 1, value=type)])
        return True

    def createFirstSheet(self, sheetName):
        self.sheet = self.client.open(sheetName).sheet1
        return self.sheet

    def createSheetById(self, sheetName, id):
        self.sheetId = self.client.open(sheetName).get_worksheet_by_id(id)
        return self.sheetId

    def createRecordsSheet(self, sheetName, id):
        self.sheetRecord = self.client.open(sheetName).get_worksheet_by_id(id)
        return self.sheetId

    def getUserIdByName(self, name) -> int:
        nameCell: gspread.Cell = self.sheetId.find(name)
        id = self.sheetId.cell(nameCell.row, nameCell.col - 1).value
        return int(id)

    def getUserNameById(self, id):
        idCell: gspread.Cell = self.sheetId.find(str(id))
        userNameCell = self.sheetId.range(idCell.row, idCell.col + 1)
        return userNameCell[0].value

    def deleteUser(self, cellString):
        row, col = gspread.utils.a1_to_rowcol(cellString)
        self.sheet.update_cells([
            gspread.cell.Cell(row, col, ""),
            gspread.cell.Cell(row, col + 1, ""),
        ])

    def isUserExist(self, id) -> bool:
        return False if self.sheetId.find(str(id)) is None else True

    def editUser(self, userId, name, lastName) -> bool:
        idCell = self.sheetId.find(str(userId))
        if not idCell:
            return False
        else:
            self.sheetId.update_cells([gspread.cell.Cell(idCell.row, idCell.col + 1, name + " " + lastName)])
            return True

    def registerUser(self, name, lastName, userId):
        idCell = self.sheetId.find(str(userId))
        if not idCell:
            self.sheetId.append_row([userId, name + " " + lastName])
        else:
            self.sheetId.update_cells([gspread.cell.Cell(idCell.row, idCell.col + 1, name + " " + lastName)])

    def addConnectedRecordMessages(self, date: datetime, messageId, userId):
        newRowIndex = next_available_row(self.sheetRecord)
        self.sheetRecord.append_row([fullDateToMachineString(date), str(messageId), str(userId),
                                     f'=TEXTJOIN(" "; TRUE;A{newRowIndex} ; B{newRowIndex} ; C{newRowIndex})'],
                                    value_input_option=ValueInputOption.user_entered)

    def deleteRecord(self, record: Record):
        for cell in record.nameCells:
            cell.value = ''

        self.sheet.update_cells(record.nameCells)

    def deleteUserFromRecords(self, userId, dateString):
        cell = self.sheetRecord.find(re.compile(f'{dateString} \d+ {userId}'), in_column=4)
        if cell:
            self.sheetRecord.delete_row(cell.row)

    def getMsgIdAndUserIdByRecordAndDelete(self, date: datetime):
        res = []
        rows = []
        userCells: list[Cell] = self.sheetRecord.findall(re.compile(fullDateToMachineString(date) + " \d+ \d+"),
                                                         in_column=4)
        if not userCells:
            print("unexpected beh, cant find date in records.table")
            return res
        for cell in userCells:
            listEl = cell.value.split(sep=" ")
            res.append((listEl[2], listEl[3]))
            rows.append(cell.row)

        self.sheetRecord.delete_rows(start_index=min(rows), end_index=max(rows))

        return res

    def getAllRecords(self) -> list[Record]:
        table_cells: list[Cell] = self.sheet.range("A1:L70")
        return takeDays(table_cells)


def takeDays(cells: list[Cell]) -> list[Record]:
    RECORD_SIZE = 6
    DAYS_INDENT = 10
    DAYS_IN_TABLE = 7
    SKIP_EMPTY_COL = 2

    def takeDay(dayIndex) -> list[Record]:
        records = []
        date = takeCell(cells, col=1, row=2 + dayIndex * DAYS_INDENT)
        for timeIndex in range(0, 5):
            recordCells = takeRange(cells,
                                    start_col=3 + timeIndex * SKIP_EMPTY_COL,
                                    end_col=3 + timeIndex * SKIP_EMPTY_COL,
                                    start_row=1 + dayIndex * DAYS_INDENT,
                                    end_row=1 + dayIndex * DAYS_INDENT + RECORD_SIZE)
            # see google sheet to know list indexes
            record = Record(dateCell=date, timeCell=recordCells[0], countCell=recordCells[1], nameCells=recordCells[2:])
            records.append(record)
        return records

    allRecords: list[Record] = []
    for dayIndex in range(0, DAYS_IN_TABLE - 1):
        dayRecords = takeDay(dayIndex)
        allRecords.extend(dayRecords)

    return allRecords


def takeCell(cells: list[Cell], col, row) -> Cell or None:
    for cell in cells:
        if cell.col == col and cell.row == row:
            return cell
    return None


def takeRange(cells: list[Cell], start_col, start_row, end_col, end_row):
    result: list[Cell] = []
    for cell in cells:
        if start_col <= cell.col <= end_col and start_row <= cell.row <= end_row:
            result.append(cell)
    return result


def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list) + 1)
