from contextlib import suppress
from datetime import datetime
import os
from queue import Queue
import shutil
import subprocess
import sys
from threading import Thread
from time import sleep
from typing import Dict, List, Optional
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget
import yaml
from galog.app.components.capture_pane import CapturePane, RunAppAction
from galog.app.components.dialogs.stop_capture_dialog import (
    StopCaptureDialog,
    StopCaptureDialogResult,
)
from galog.app.controllers.capture_pane import CapturePaneController
from galog.app.controllers.kill_app.controller import KillAppController
from galog.app.controllers.log_messages_pane.controller import (
    LogMessagesPaneController,
)
from galog.app.controllers.log_messages_pane.log_reader import (
    AndroidAppLogReader,
    LogLine,
    ProcessEndedEvent,
    ProcessStartedEvent,
)
from galog.app.controllers.run_app.controller import RunAppController
from galog.app.device.device import AdbClient
from galog.app.highlighting_rules import HighlightingRules
from galog.app.components.message_view_pane import LogMessageViewPane
from galog.app.util.messagebox import showNotImpMsgBox, showQuitMsgBox
from galog.app.util.style import CustomStyle

from galog.app.util.paths import HIGHLIGHTING_RULES_FILE, STYLES_DIR, iconFile

from .. import app_strings

from .log_messages_pane import LogMessagesPane

ADB_HOST = "127.0.0.1"
ADB_PORT = 5037


class MainWindow(QMainWindow):
    _viewWindows: List[LogMessageViewPane]
    _liveReload: bool

    def __init__(self) -> None:
        super().__init__()
        self._searchPane = None
        self._liveReload = True
        self.capturePaneController = CapturePaneController(ADB_HOST, ADB_PORT)
        self.logMessagesPaneController = LogMessagesPaneController(ADB_HOST, ADB_PORT)
        self.startAdbServer()
        self.loadAppStrings()
        self.loadStyleSheet()
        self.initHighlighting()
        self.initUserInterface()
        self.setStyle(CustomStyle())

    def startAdbServer(self):
        adb = shutil.which("adb")
        if not adb:
            return

        def execAdbServer():
            with suppress(subprocess.SubprocessError):
                subprocess.call(
                    args=[adb, "server"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )

        QThreadPool.globalInstance().start(execAdbServer)

    def loadAppStrings(self):
        app_strings.init("en")

    def styleSheetFiles(self, path: str = STYLES_DIR):
        result = []
        for entry in os.scandir(path):
            if entry.is_file() and entry.path.endswith(".qss"):
                result.append(entry.path)
            elif entry.is_dir():
                result.extend(self.styleSheetFiles(entry.path))

        return result

    def loadStyleSheet(self):
        style = ""
        for filepath in self.styleSheetFiles():
            with open(filepath, "r", encoding="utf-8") as f:
                style += f.read() + "\n"

        self.setStyleSheet(style)

    def initHighlighting(self):
        rules = HighlightingRules()
        with open(HIGHLIGHTING_RULES_FILE) as f:
            content = yaml.load_all(f, yaml.SafeLoader)
            rules.load(content)

        self.logMessagesPaneController.setHighlightingRules(rules)

    def closeEvent(self, event: QEvent):
        if showQuitMsgBox():
            self.logMessagesPaneController.stopCapture()
            event.accept()
        else:
            event.ignore()

    def setCaptureSpecificActionsEnabled(self, enabled: bool):
        menuBar = self.menuBar()
        for fileMenu in menuBar.findChildren(QMenu):
            for action in fileMenu.actions():
                if action.data() == True:
                    action.setEnabled(enabled)

    def startCapture(self):
        capturePane = CapturePane(self)
        self.capturePaneController.takeControl(capturePane)
        self.capturePaneController.startCaptureDialog()

        if self.capturePaneController.captureTargetSelected():
            device = self.capturePaneController.selectedDevice()
            package = self.capturePaneController.selectedPackage()
            action = self.capturePaneController.selectedAction()

            if action != RunAppAction.DoNotStartApp:
                controller = RunAppController(ADB_HOST, ADB_PORT)
                controller.setAppDebug(action == RunAppAction.StartAppDebug)
                controller.runApp(device, package)

            self.logMessagesPaneController.startCapture(device, package)
            self.setCaptureSpecificActionsEnabled(True)

    def stopCapture(self):
        dialog = StopCaptureDialog()
        result = dialog.exec_()
        if result == StopCaptureDialogResult.Rejected:
            return

        if result == StopCaptureDialogResult.AcceptedKillApp:
            device = self.logMessagesPaneController.device
            package = self.logMessagesPaneController.package
            controller = KillAppController(ADB_HOST, ADB_PORT)
            controller.killApp(device, package)

        self.logMessagesPaneController.stopCapture()
        self.setCaptureSpecificActionsEnabled(False)

    def toggleMessageFilter(self):
        if self.logMessagesPaneController.messageFilterEnabled():
            self.logMessagesPaneController.disableMessageFilter()
        else:
            self.logMessagesPaneController.enableMessageFilter()


    def startCaptureAction(self):
        action = QAction("&New", self)
        action.setShortcut("Ctrl+N")
        action.setStatusTip("Start new log capture")
        action.triggered.connect(lambda: self.startCapture())
        action.setEnabled(True)
        action.setData(False)
        return action

    def toggleMessageFilterAction(self):
        action = QAction("&Find", self)
        action.setShortcut("Ctrl+F")
        action.setStatusTip("Toggle message filter mode")
        action.triggered.connect(lambda: self.toggleMessageFilter())
        action.setEnabled(True)
        action.setData(False)
        return action

    def clearCapturedLogsAction(self):
        action = QAction("&Clear", self)
        action.setShortcut("Ctrl+X")
        action.setStatusTip("Clear captured logs")
        action.triggered.connect(lambda: showNotImpMsgBox())
        action.setEnabled(False)
        action.setData(True)
        return action

    def stopCaptureAction(self):
        action = QAction("&Stop", self)
        action.setShortcut("Ctrl+Q")
        action.setStatusTip("Stop capture")
        action.triggered.connect(lambda: self.stopCapture())
        action.setEnabled(False)
        action.setData(True)
        return action

    def openLogFileAction(self):
        action = QAction("&Open", self)
        action.setShortcut("Ctrl+O")
        action.setStatusTip("Open log capture from file")
        action.triggered.connect(lambda: showNotImpMsgBox())
        action.setEnabled(True)
        action.setData(False)
        return action

    def saveLogFileAction(self):
        action = QAction("&Save", self)
        action.setShortcut("Ctrl+S")
        action.setStatusTip("Save log capture to file")
        action.triggered.connect(lambda: showNotImpMsgBox())
        action.setEnabled(False)
        action.setData(True)
        return action

    def installApkAction(self):
        action = QAction("&Install APK", self)
        action.setShortcut("Ctrl+I")
        action.setStatusTip("Install APK file")
        action.triggered.connect(lambda: showNotImpMsgBox())
        action.setEnabled(True)
        action.setData(False)
        return action

    def takeScreenshotAction(self):
        action = QAction("&Take screenshot", self)
        action.setShortcut("Ctrl+P")
        action.setStatusTip("Take screenshot")
        action.triggered.connect(lambda: showNotImpMsgBox())
        action.setEnabled(False)
        action.setData(True)
        return action

    def setupMenuBar(self):
        menuBar = self.menuBar()
        captureMenu = menuBar.addMenu("📱 &Capture")
        captureMenu.addAction(self.startCaptureAction())
        captureMenu.addAction(self.stopCaptureAction())
        captureMenu.addAction(self.clearCapturedLogsAction())
        captureMenu.addAction(self.openLogFileAction())
        captureMenu.addAction(self.saveLogFileAction())
        captureMenu.addAction(self.toggleMessageFilterAction())

        adbMenu = menuBar.addMenu("🐞 &ADB")
        adbMenu.addAction(self.installApkAction())
        adbMenu.addAction(self.takeScreenshotAction())

    def initUserInterface(self):
        screen = QApplication.desktop().screenGeometry()
        width = int(screen.width() * 0.8)
        height = int(screen.height() * 0.8)
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

        pane = LogMessagesPane(self)
        self.logMessagesPaneController.takeControl(pane)
        self.setCentralWidget(pane)
        self.setWindowTitle("galog")
        self.setWindowIcon(QIcon(iconFile("galog")))

        self.setupMenuBar()
        self.statusBar().show()