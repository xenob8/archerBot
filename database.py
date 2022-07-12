import builtins
from datetime import datetime, timedelta
import itertools
import re

from oauth2client.service_account import ServiceAccountCredentials
import gspread
from gspread import Cell
import numpy as np
from gspread.utils import ValueRenderOption, ValueInputOption
import config
from record import Record


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
        self.sheet.update_cells(
            [Cell(row=cell.row, col=cell.col, value=username), Cell(row=cell.row, col=cell.col + 1, value=type)])

    def createFirstSheet(self, sheetName):
        self.sheet = self.client.open(sheetName).sheet1
        return self.sheet

    def createSheetById(self, sheetName, id):
        self.sheetId = self.client.open(sheetName).get_worksheet_by_id(id)
        return self.sheetId

    def createRecordsSheet(self, sheetName, id):
        self.sheetRecord = self.client.open(sheetName).get_worksheet_by_id(id)
        return self.sheetId


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

    def getUsersIdByTime(self, dayIndex: int, timeIndex: int) -> list:
        names_cells = self.sheet.range("names" + str(dayIndex))[timeIndex * 2::self.MAX_TIMES]
        print(names_cells)
        ids = []
        for name_cell in names_cells:
            name = name_cell.value
            if not name:
                continue
            else:
                ids.append(self.getUserIdByName(name))
        return ids

    def deleteUsersByTime(self, dayIndex: int, timeIndex: int):
        names_cells: list[Cell] = self.sheet.range("names" + str(dayIndex))[timeIndex * 2::self.MAX_TIMES]
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

    def addRecord(self, userId, dayIndex, timeIndex, messageId):
        newRowIndex = next_available_row(self.sheetRecord)
        self.sheetRecord.append_row([userId, dayIndex, timeIndex, messageId,
                                     f'=TEXTJOIN(" "; TRUE;A{newRowIndex} ; B{newRowIndex})',
                                     f'=TEXTJOIN(" "; TRUE;A{newRowIndex} ; B{newRowIndex};C{newRowIndex})'],
                                    value_input_option=ValueInputOption.user_entered)

    def deleteRecord(self, id: int, dayIndex: int, timeIndex: int) -> str:
        cell: Cell = self.sheetRecord.find(str(id) + " " + str(dayIndex) + " " + str(timeIndex), in_column=6)
        if cell:
            mess = self.sheetRecord.cell(row=cell.row, col=self.MESSAGE_ID_COL).value
            self.sheetRecord.delete_row(index=cell.row)
            return mess

    def deleteRecordByMessageId(self, messageId):
        messCell: Cell = self.sheetRecord.find(str(messageId), in_column=4)
        if messCell:
            self.sheetRecord.delete_row(messCell.row)

    def deleteTime(self, dayIndex, timeIndex):
        cells = self.sheet.range("times" + str(dayIndex))
        delCell = cells[timeIndex * 2]
        self.sheet.update_cell(delCell.row, delCell.col, "")

    # def findUserTimesByIdAndDay(self, userId, dayIndex):
    #     cells = self.sheetRecord.findall(str(userId) + " " + str(dayIndex))
    #     times = []
    #     if cells:
    #         for cell in cells:
    #             times.append(self.sheetRecord.cell(cell.row, cell.col - 2).value)
    #     return times

    def getUserDaysAndTimesById(self, userId):
        userCells: list[Cell] = self.sheetRecord.findall(re.compile(str(userId) + " \d \d"), in_column=6)
        map: dict[int, list[int]] = {}
        if userCells:
            print(userCells)
            for cell in userCells:
                intList = list(builtins.map(int, cell.value.split(sep=" ")))
                if map.get(intList[1]):
                    map[intList[1]].append(intList[2])
                else:
                    map[intList[1]] = [intList[2]]
        return map

    def getAllRecords(self) -> list[Record]:
        table_cells: list[Cell] = self.sheet.range("A1:L70")
        print(table_cells)

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
                                    start_col=3 + timeIndex*SKIP_EMPTY_COL,
                                    end_col=3 + timeIndex*SKIP_EMPTY_COL,
                                    start_row=1 + dayIndex * DAYS_INDENT,
                                    end_row=1 + dayIndex * DAYS_INDENT + RECORD_SIZE)
            # see google sheet to know list indexes
            print("day record cell times:", recordCells[0])
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
