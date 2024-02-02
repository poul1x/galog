from enum import Enum, auto

from PyQt5.QtGui import QStandardItem, QStandardItemModel

# ro.product.cpu.abi arm/arm64
# ro.product.model # ro.product.manufacturer (ro.product.name)
# Android ver adb shell getprop ro.build.version.release
# API level adb shell getprop ro.build.version.sdk
# API min level ro.build.version.min_supported_target_sdk
# Google Pixel 4a (sunfish)
# Android 12 (API Level: 23-31)
# arm-v64


class Columns(int, Enum):
    deviceSerial = 0
    deviceName = auto()
    buildInfo = auto()
    cpuAbi = auto()


class DataModel(QStandardItemModel):
    def __init__(self):
        super().__init__(0, len(Columns))
        labels = ["Device Serial", "Device name", "Build info", "CPU ABI"]
        self.setHorizontalHeaderLabels(labels)

    def append(
        self,
        itemDeviceSerial: QStandardItem,
        itemDeviceName: QStandardItem,
        itemBuildInfo: QStandardItem,
        itemCpuAbi: QStandardItem,
    ):
        self.appendRow(
            [
                itemDeviceSerial,
                itemDeviceName,
                itemBuildInfo,
                itemCpuAbi,
            ]
        )
