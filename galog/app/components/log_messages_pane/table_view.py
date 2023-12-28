from typing import Optional
from PyQt5 import QtCore

from PyQt5.QtCore import QRect, Qt, QSize
from PyQt5.QtGui import QColor, QFont, QPainter, QFontMetrics, QFocusEvent
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableView,
    QWidget,
    QProxyStyle,
    QStyle,
)

from galog.app.util.painter import painterSaveRestore

from .delegate import StyledItemDelegate
from .filter_model import FilterModel
from .data_model import Columns, DataModel


class VerticalHeader(QHeaderView):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(Qt.Vertical, parent)
        self._font = QFont()
        self._font.setPixelSize(19)
        self._font.setFamily("Arial")
        self._font.setWeight(QFont.Bold)

    def _selectedRows(self):
        return [index.row() for index in self.selectionModel().selectedRows()]

    def paintSection(self, _painter: QPainter, rect: QRect, index: int):
        align = Qt.AlignCenter
        lightColor = QColor("#FFFFFF")
        darkColor = QColor("#464646")

        with painterSaveRestore(_painter) as painter:
            if index in self._selectedRows():
                painter.fillRect(rect, darkColor)
                painter.setPen(lightColor)
            else:
                painter.fillRect(rect, lightColor)
                painter.setPen(darkColor)

            painter.setFont(self._font)
            painter.drawText(rect, align, str(index + 1))

    def sizeHint(self) -> QSize:
        fm = QFontMetrics(self._font)
        rowNum = self.model().rowCount()
        return QSize(fm.width(str(rowNum)) + 5, 0)


class TableView(QTableView):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.initCustomDelegate()
        self.initUserInterface()

    def initCustomDelegate(self):
        self.delegate = StyledItemDelegate(self)
        self.setItemDelegate(self.delegate)

    def focusInEvent(self, event: QFocusEvent):
        # Automatically select first row on focus with TAB key
        super().focusInEvent(event)
        if self.filterModel.rowCount() > 0:
            if not self.selectedIndexes():
                self.selectRow(0)

    def initUserInterface(self):
        self.dataModel = DataModel()
        self.filterModel = FilterModel()
        self.filterModel.setSourceModel(self.dataModel)
        self.setModel(self.filterModel)

        self.setCornerButtonEnabled(False)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)
        self.setTabKeyNavigation(False)
        self.setShowGrid(False)

        hHeader = self.horizontalHeader()
        hHeader.setSectionResizeMode(Columns.logMessage, QHeaderView.Stretch)
        hHeader.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setColumnWidth(Columns.logLevel, 10)
        self.setColumnWidth(Columns.tagName, 200)

        font = self.delegate.font()
        height = QFontMetrics(font).height()
        height += 5  # vertical padding

        vHeader = VerticalHeader(self)
        self.setVerticalHeader(vHeader)
        vHeader.setSectionResizeMode(QHeaderView.Fixed)
        vHeader.setMinimumSectionSize(height)
        vHeader.setDefaultSectionSize(height)
        vHeader.setVisible(False)
