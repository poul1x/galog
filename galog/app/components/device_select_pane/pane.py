from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QStandardItem
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget, QDialog, QApplication, QComboBox
from galog.app.components.capture_pane.body import SearchInputCanActivate

from galog.app.components.reusable.search_input.widget import SearchInput
from galog.app.util.hotkeys import HotkeyHelper

from .table_view import TableView

from .header import DeviceSelectPaneHeader
from .footer import DeviceSelectPaneFooter


class DeviceSelectPane(QDialog):
    toggleMessageFilter = pyqtSignal()
    copyRowsToClipboard = pyqtSignal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("DeviceSelectPane")
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()
        self.dataModel.append(
            QStandardItem("RF8T213A4YW"),
            QStandardItem("Google Pixel 4a (sunfish)"),
            QStandardItem("Android 12 (API Level: 23-31)"),
            QStandardItem("arm-v64"),
        )

        self.dataModel.append(
            QStandardItem("nm87weerty4"),
            QStandardItem("Samsung SM-M127F (m12nsxx)"),
            QStandardItem("Android 12 (API Level: ?-?)"),
            QStandardItem("arm-v64"),
        )

        self.dataModel.append(
            QStandardItem("ert45tgf"),
            QStandardItem("Error: failed to get XXXX"),
            QStandardItem(""),
            QStandardItem(""),
        )

        self.tableView.setSpan(2, 1, 1, self.dataModel.columnCount())
        self.setGeometryAuto()

    # def keyPressEvent(self, event: QKeyEvent):
    #     helper = HotkeyHelper(event)
    #     if helper.isEscapePressed():
    #         self.toggleMessageFilter.emit()
    #     elif helper.isCtrlCPressed():
    #         self.copyRowsToClipboard.emit()
    #     else:
    #         super().keyPressEvent(event)

    def initUserInterface(self):
        self.tableView = TableView(self)
        self.dataModel = self.tableView.dataModel
        self.filterModel = self.tableView.filterModel



        layout = QVBoxLayout()
        layout.addWidget(DeviceSelectPaneHeader(self))
        layout.addWidget(self.tableView)

        layout2 = QHBoxLayout()

        # layout.addWidget(self.tableView, 1)
        self.searchInput = SearchInputCanActivate(self)
        self.searchInput.setPlaceholderText("Search device by serial")
        layout2.addWidget(self.searchInput, 1)

        self.searchTypeDropdown = QComboBox(self)
        self.searchTypeDropdown.addItem("Serial")
        self.searchTypeDropdown.addItem("Name")
        layout2.addWidget(self.searchTypeDropdown)

        layout.addLayout(layout2)
        layout.addWidget(DeviceSelectPaneFooter(self))
        self.setLayout(layout)

        # self.searchPane.button.setFocusPolicy(Qt.NoFocus)
        # self.searchPane.input.setFocusPolicy(Qt.NoFocus)
        # self.tableView.setFocusPolicy(Qt.StrongFocus)
        # self.tableView.setFocus()

        # self.setTabOrder(self.tableView, self.searchPane.input)
        # self.setTabOrder(self.searchPane.input, self.tableView)

    def setGeometryAuto(self):
        screen = QApplication.desktop().screenGeometry()
        width = int(screen.width() * 0.4)
        height = int(screen.height() * 0.4)
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)
