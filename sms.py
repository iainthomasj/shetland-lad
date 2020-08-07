import serial
import time

class TextMessage:
    def __init__(self, recipient="*******3023", message="Fire and Rescue Service required for a reported fire in a detached garage, 48 Fogralea, Lerwick, Shetland Isles, ZE10SE."):
        self.recipient = recipient
        self.content = message

    def setRecipient(self, number):
        self.recipient = number

    def setContent(self, message):
        self.content = message

    def connectPhone(self):
        self.ser = serial.Serial('/dev/ttyUSB0', 460800, timeout=5)
        time.sleep(1)

    def sendMessage(self):
        self.ser.write('ATZ\r'.encode())
        time.sleep(1)
        self.ser.write('AT+CMGF=1\r'.encode())
        time.sleep(1)
        temp = '''AT+CMGS="''' + self.recipient + '''"\r'''
        self.ser.write(temp.encode())
        time.sleep(1)
        temp = self.content + "\r"
        self.ser.write(temp.encode())
        time.sleep(1)
        temp = chr(26)
        self.ser.write(temp.encode())
        time.sleep(1)

    def disconnectPhone(self):
        self.ser.close()

if __name__ == "__main__":
    tm = TextMessage("*******3023", "Fire and Rescue Service required for a reported fire in a detached garage, 48 Fogralea, Lerwick, Shetland Isles, ZE10SE.")
    tm.connectPhone()
    try:
        tm.sendMessage()
    except Exception as e:
        print (e)
        
    tm.disconnectPhone()
