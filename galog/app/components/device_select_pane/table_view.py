from typing import Optional

from PyQt5.QtCore import QRect, QSize, Qt, QSortFilterProxyModel
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QPainter
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QTableView, QWidget

from galog.app.util.painter import painterSaveRestore
from galog.app.util.table_view import TableView as BaseTableView

from .data_model import Columns, DataModel


class TableView(BaseTableView):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.initUserInterface()

    def initUserInterface(self):
        self.dataModel = DataModel()
        self.filterModel = QSortFilterProxyModel()
        self.filterModel.setDynamicSortFilter(True)
        self.filterModel.setFilterKeyColumn(Columns.deviceName)
        self.filterModel.setSourceModel(self.dataModel)
        self.setModel(self.filterModel)

        self.setCornerButtonEnabled(False)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)
        self.setTabKeyNavigation(False)
        self.setShowGrid(False)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)


        hHeader = self.horizontalHeader()
        hHeader.setSectionResizeMode(Columns.deviceSerial, QHeaderView.Interactive)
        hHeader.setSectionResizeMode(Columns.deviceName, QHeaderView.Interactive)
        hHeader.setSectionResizeMode(Columns.buildInfo, QHeaderView.Interactive)
        hHeader.setSectionResizeMode(Columns.cpuAbi, QHeaderView.Stretch)
        hHeader.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        font = QFont("Arial")
        font.setPixelSize(19)
        self.setFont(font)

        fontMetrics = QFontMetrics(font)
        self.setColumnWidth(Columns.deviceSerial, fontMetrics.width("A" * 12))
        self.setColumnWidth(Columns.deviceName, fontMetrics.width("a" * 30))
        self.setColumnWidth(Columns.buildInfo, fontMetrics.width("a" * 30))
        # self.resizeColumnsToContents()

        vHeader = self.verticalHeader()
        vHeader.setVisible(False)