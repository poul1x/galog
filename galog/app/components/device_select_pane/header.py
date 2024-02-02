from enum import Enum, auto

from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QIcon, QIntValidator, QRegExpValidator
from PyQt5.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QWidget, QLineEdit

from galog.app.util.paths import iconFile

PORT_REGEXP = r"^(?![7-9]\d\d\d\d)(?!6[6-9]\d\d\d)(?!65[6-9]\d\d)(?!655[4-9]\d)(?!6553[6-9])(?!0+)\d{1,5}$"
IP_REGEXP = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"

class DeviceSelectPaneHeader(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("DeviceSelectPaneHeader")
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()

    def initUserInterface(self):
        layout = QHBoxLayout()
        layoutLeft = QHBoxLayout()
        layoutLeft.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layoutRight = QHBoxLayout()
        layoutRight.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.deviceLabel = QLabel(self)
        self.deviceLabel.setText("ADB Server IPv4 address:")
        layoutLeft.addWidget(self.deviceLabel)

        self.deviceDropDown = QLineEdit(self)
        layoutLeft.addWidget(self.deviceDropDown)
        self.deviceDropDown.setValidator(QRegExpValidator(QRegExp(IP_REGEXP)))


        self.reloadButton = QPushButton(self)
        self.reloadButton.setIcon(QIcon(iconFile("reload")))
        self.reloadButton.setText("Reload devices")
        layoutRight.addWidget(self.reloadButton)

        self.actionLabel = QLabel(self)
        self.actionLabel.setText("Port:")
        layoutLeft.addWidget(self.actionLabel)

        self.actionDropDown = QLineEdit(self)
        layoutLeft.addWidget(self.actionDropDown)
        # self.actionDropDown.setValidator(QIntValidator(0, 100, self) )
        self.actionDropDown.setValidator(QRegExpValidator(QRegExp(PORT_REGEXP)))



        layout.addLayout(layoutLeft)
        layout.addLayout(layoutRight)
        self.setLayout(layout)
