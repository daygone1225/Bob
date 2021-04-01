import base64
import serial


class HC05Serial(serial.Serial):
    def __init__(self, device: str):
        super().__init__(device, 38400, timeout=1, parity=serial.PARITY_NONE)

    def writeLine(self, msg: str):
        self.write((msg + "\n").encode("UTF-8"))

    def writeBase64Line(self, msg: str):
        encoded_str = base64.b64encode(msg.encode("UTF-8"))
        print("sned:\t", encoded_str)
        print(self.dumpArray(encoded_str))
        self.write(encoded_str)
        self.write("\n".encode("UTF-8"))

    def dumpArray(self,array:bytes)->str:
        stra="["
        for b in array:
            stra=stra+str(b)+","

        return stra+"]"