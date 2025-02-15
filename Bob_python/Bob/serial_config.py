import re

import serial
from serial import Serial
from serial.tools.list_ports_linux import comports

from Bob.communication.framework.fw_package_device import PackageDevice
from Bob.device.concrete.crt_serial_dev import LocalSerialDevice
from Bob.communication.concrete.crt_package_device import SerialPackageDevice
from Bob.robot.concrete.crt_robot import SerialRobot, BytePrintedRobot
from Bob.robot.framework.fw_robot import Robot


def getBTSerial(device):
    return LocalSerialDevice(
        serial.Serial(device, baudrate=38400, parity=serial.PARITY_NONE, timeout=0.5, write_timeout=1),
        write_delay_ms=0)


def getRobotSerial(device):
    return LocalSerialDevice(Serial(device, baudrate=57142, timeout=0.5, write_timeout=100),
                             write_delay_ms=100)


def getBluetoothPackageDeviceWithDescription(description: str) -> PackageDevice:
    for port in comports():
        if re.search(description, port.description):
            ser = SerialPackageDevice(getBTSerial(port.device))
            ser.open()
            return ser

    raise Exception(description + " not found.")


def getBluetoothPackageDeviceWithName(name: str) -> PackageDevice:
    ser = SerialPackageDevice(getBTSerial(name))
    ser.open()
    return ser


def getRobotWithDescription(description: str) -> Robot:
    for port in comports():
        if re.search(description, port.description):
            bot = SerialRobot(getRobotSerial(port.device))
            if not bot.isOpen():
                bot.open()
            return bot

    raise Exception(description + " not found.")


def getRobotWithName(name: str):
    bot = SerialRobot(getRobotSerial(name))
    if not bot.isOpen():
        bot.open()
    return bot


def getPrintedRobot() -> Robot:
    bot = BytePrintedRobot()
    if not bot.isOpen():
        bot.open()
    return bot
