import os

from Bob.detector.concrete.object_detect_yolov5 import ObjectDetector
from Bob.detector.concrete.face_detect_deepface import FaceDetector
from Bob.dbctrl.concrete.crt_database import JSONDatabase
from Bob.robot.concrete.crt_action import CSVAction
from Bob.robot.framework.fw_action import Action
from Bob.serial_config import *
import base64
import json
from typing import List, Optional
from serial import SerialTimeoutException
from Bob.communication.concrete.crt_package import StringPackage, Base64LinePackage
from Bob.communication.framework.fw_listener import PackageListener
from Bob.communication.framework.fw_package_device import PackageDevice
from Bob.detector.framework.detector import DetectListener

obj_db_location = f"db{os.path.sep}objects.json"
face_db_location = f"db{os.path.sep}faces.json"
db_charset = 'UTF-8'

object_db = JSONDatabase(open(obj_db_location, encoding=db_charset))
face_db = JSONDatabase(open(face_db_location, encoding=db_charset))

bt_description = ".*CP2102.*"
bot_description = ".*FT232R.*"

# robot = getRobotWithName("COM1")
# robot = getRobotWithDescription(bot_description)
robot = getPrintedRobot()

detector = None
monitor = None


def getActionFromFileName(file: str) -> Action:
    return CSVAction(f'actions{os.path.sep}{file}')


class CommandControlListener(PackageListener):
    def __init__(self, device: PackageDevice):
        self.__id_counter = 0
        self.package_device = device
        self.mode: str = ""

    def onReceive(self, data: bytes):
        global detector
        d = base64.decodebytes(data)
        cmd = d.decode()
        print("receive:", cmd)

        if cmd == "DETECT_OBJECT":
            if detector is not None:
                detector.stop()

            detector = ObjectDetector(ObjectDetectListener(self.package_device))
            detector.start()
            self.mode = cmd

        elif cmd == "DETECT_FACE":
            if detector is not None:
                detector.stop()

            detector = FaceDetector(FaceDetectListener(self.package_device))
            detector.start()
            self.mode = cmd
        elif cmd == "DETECT_INTER_OBJECT":
            if detector is not None:
                detector.stop()

            detector = ObjectDetector(InteractiveObjectDetectListener(self.package_device))
            detector.start()
            self.mode = cmd

        elif cmd == "START_DETECT":
            print("Start detect")
            if detector is None:
                return
            detector.resume()
        elif cmd == "PAUSE_DETECT":
            if detector is None:
                return
            print("Pause detect")
            detector.pause()
        elif cmd == "STOP_DETECT":
            if detector is not None:
                detector.stop()

        elif cmd == "DB_GET_ALL":
            all_data: json = object_db.getAllData()
            sendData = {"id": self.__id_counter, "response_type": "json_object", "content": "all_object",
                        "data": all_data}
            jsonString = json.dumps(sendData, ensure_ascii=False)
            print("Send:", jsonString)
            self.package_device.writePackage(Base64LinePackage(StringPackage(jsonString, "UTF-8")))
            self.__id_counter = self.__id_counter + 1


class FaceDetectListener(DetectListener):
    def __init__(self, device: PackageDevice):
        self.device = device

    def onDetect(self, face_type: str):
        print("now face emotion: " + face_type)
        obj: Optional[json] = face_db.queryForId(face_type)
        if obj is not None:
            data: json = obj['data']
            sendData = {"id": -1, "response_type": "json_object", "content": "single_object", "data": data}
            jsonString = json.dumps(sendData, ensure_ascii=False)
            print("Send:", jsonString)
            self.device.writePackage(Base64LinePackage(StringPackage(jsonString, "UTF-8")))


class ObjectDetectListener(DetectListener):
    def __init__(self, device: PackageDevice):
        self.device = device

    def onDetect(self, objectList: List):
        for dobj in objectList:
            if dobj['confidence'] < 0.65:
                continue

            obj: Optional[json] = object_db.queryForId(dobj['name'])
            if obj is not None:
                data: json = obj['data']
                sendData = {"id": -1, "response_type": "json_object", "content": "single_object", "data": data}
                jsonString = json.dumps(sendData, ensure_ascii=False)
                print("Send:", jsonString)

                self.device.writePackage(Base64LinePackage(StringPackage(jsonString, "UTF-8")))

                if robot.isOpen():
                    try:
                        robot.doAction(getActionFromFileName(data['action']))
                        robot.doAction(getActionFromFileName("reset.csv"))
                    except SerialTimeoutException:
                        print("robot serial timeout")

                break


class InteractiveObjectDetectListener(DetectListener):
    def __init__(self, device: PackageDevice):
        self.device = device

    def onDetect(self, objectList: List):
        for dobj in objectList:
            if dobj['confidence'] < 0.65:
                continue

            obj: Optional[json] = object_db.queryForId(dobj['name'])
            if obj is not None:
                data: json = obj['data']
                sendData = {"id": -1, "response_type": "json_object", "content": "single_object", "data": data}
                jsonString = json.dumps(sendData, ensure_ascii=False)
                print("Send:", jsonString)
                self.device.writePackage(Base64LinePackage(StringPackage(jsonString, "UTF-8")))
                break
