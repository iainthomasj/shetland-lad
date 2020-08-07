"""
sms.py - Used to send txt messages.
"""
import serial
import time

class TextMessage:
    def __init__(self, recipient="???????????", message="Hello World"):
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
    tm = TextMessage("07884003023", "Hello Iain")
    tm.connectPhone()
    try:
        tm.sendMessage()
    except Exception as e:
        print (e)
        
    tm.disconnectPhone()
