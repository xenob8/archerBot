from datetime import *

from gspread import Cell



class Record:
    date: datetime or None

    def __init__(self, dateCell: Cell, timeCell: Cell, countCell: Cell, nameCells: list[Cell]):
        def makeDate():
            if self.dateCell.value:
                if self.timeCell.value:
                    return datetime.strptime(self.dateCell.value + " " + self.timeCell.value, "%d.%m.%Y %H:%M")
                else:
                    return datetime.strptime(self.dateCell.value, "%d.%m.%Y")

        self.dateCell = dateCell
        self.timeCell = timeCell
        self.countCell = countCell
        self.nameCells = nameCells
        self.date = makeDate()

    def getCount(self):
        if self.countCell.value:
            return int(self.countCell.value)

    def getFreeNameCell(self) -> Cell:
        for nameCell in self.nameCells:
            if not nameCell.value:
                return nameCell
