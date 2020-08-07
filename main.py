import os
import sys
import time
from time import sleep
import glob
import socket
from pygame import mixer 
import threading
import RPi.GPIO as GPIO

from sms import TextMessage


reset_pin = 12
evacuation_pin = 22
buzzer_pin = 23
beacon_pin = 24
all_clear_pin = 26

TEMP_CHECK_INTERVAL = 1
RST_CHECK_INTERVAL = 1

STATUS = 0  # 0 -> No Fire || 1 -> Fire Detected

PHONE_NUMBER = "07884003023"
MESSAGE = """ Fire Fire Fire at Location X
"""

textmessage = TextMessage(PHONE_NUMBER, MESSAGE)
textmessage.connectPhone()

def setup():
    global reset_pin, evacuation_pin, buzzer_pin, beacon_pin, all_clear_pin
    
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM) 

    #Buzzer Setup (RS PRO 96 dB Piezo Buzzer)
    GPIO.setup(buzzer_pin, GPIO.OUT)
    GPIO.output(buzzer_pin, GPIO.LOW)
        
    # LED Beacon Setup (Fulleon 600111FUL-0000)
    GPIO.setup(beacon_pin, GPIO.OUT)
    GPIO.output(beacon_pin, GPIO.LOW)
        
    #Evacuation Message Setup (ISD1820 Voice Recorder)
    GPIO.setup(evacuation_pin, GPIO.OUT)
    GPIO.output(evacuation_pin, GPIO.LOW)

    #All Clear Message Setup (ISD1820 Voice Recorder)
    GPIO.setup(all_clear_pin, GPIO.OUT)
    GPIO.output(all_clear_pin, GPIO.LOW)

    #Reset Button Setup (Tactile Switch)
    GPIO.setup(reset_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)




base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
 
# A function that reads the DS18B20 sensors data

def read_temp_raw():
    f = open(device_file, 'r') # Opens the temperature device file
    lines = f.readlines() # Returns the text
    f.close()
    return lines
 
# Convert the value of the sensor into a temperature

def read_temp():
    lines = read_temp_raw() # Read the temperature 'device file'

    # While the first line does not contain 'YES', wait for 0.2s
    # and then read the device file again.
  
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.1)
        lines = read_temp_raw()
 
    # Look for the position of the '=' in the second line of the
    # device file.
  
    equals_pos = lines[1].find('t=')
 
    # If the '=' is found, convert the rest of the line after the
    # '=' into degrees Celsius, then degrees Fahrenheit
  
    if equals_pos != -1:
      temp_string = lines[1][equals_pos+2:]
      temp_c = float(temp_string) / 1000.0
      temp_f = temp_c * 9.0 / 5.0 + 32.0
      return temp_c#, temp_f
    return 0
#Print out the temperature until the program is stopped
    
def startBuzzerSound():
    global RST_CHECK_INTERVAL, STATUS,\
           evacuation_pin, buzzer_pin, beacon_pin, reset_pin


    while STATUS:
        GPIO.output(buzzer_pin, 1)
        time.sleep(6)
        GPIO.output(buzzer_pin, 0)
        
        GPIO.output(evacuation_pin, 1)
        time.sleep(10)
        GPIO.output(evacuation_pin, 0)

    GPIO.output(buzzer_pin, 0)

def blinkLED():
    global beacon_pin, STATUS
    
    while STATUS: # Valid if STATUS != 0
        GPIO.output(beacon_pin, 1)
        time.sleep(2)
        GPIO.output(beacon_pin, 0)
        time.sleep(2) 

def checkResetSwitchUtil():
    global STATUS, RST_CHECK_INTERVAL, reset_pin
    
    while GPIO.input(reset_pin):
        #print ("in switch thread",  GPIO.input(reset_pin)) 
        time.sleep(RST_CHECK_INTERVAL)

    STATUS = 0

def checkResetSwitch():
    checkResetThread = threading.Thread(target=checkResetSwitchUtil)
    return checkResetThread

def fireDetected():
    global STATUS, textmessage
    
    STATUS = 1
    blink_led = threading.Thread(target=blinkLED)
    blink_led.start()
    textmessage.sendMessage()
    checkResetThread = checkResetSwitch()
    
    checkResetThread.start()
    startBuzzerSound()

def main():
    global TEMP_CHECK_INTERVAL

    while True:
        while read_temp() < 25:
            print (read_temp())
            time.sleep(TEMP_CHECK_INTERVAL)

        fireDetected()
        print ("Reset Done", read_temp())
        time.sleep(10)

if __name__ == "__main__":
    setup()
    main()

    textmessage.disconnectPhone()
