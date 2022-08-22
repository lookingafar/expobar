#!/usr/bin/python
# -*- coding: UTF-8 -*-
#import chardet
import os
import sys 
import time
import datetime
import logging
import spidev as SPI
sys.path.append("..")
from lib import LCD_2inch
from PIL import Image,ImageDraw,ImageFont,ImageColor
from w1thermsensor import W1ThermSensor, Sensor

#HX711 stuff
EMULATE_HX711=False

referenceUnit = 464.078

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711

def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    print("Bye!")
    sys.exit()

hx = HX711(5, 6)

hx.set_reference_unit(referenceUnit)

hx.reset()

hx.tare()

print("Tare done! Add weight now...")


# Raspberry Pi pin configuration:
RST = 27
DC = 25
BL = 18
bus = 0 
device = 0 
logging.basicConfig(level=logging.DEBUG)
try:
    #Humidity and environment temperature sensors
#    dhtSensor = Adafruit_DHT.DHT22
    dhtPin = 23
#    humidity, envTemperature = Adafruit_DHT.read_retry(dhtSensor, dhtPin)

    #Temperature Sensors
    sensor1 = W1ThermSensor(Sensor.DS18B20, "3c0107d67cb6")
#    sensor2 = W1ThermSensor(Sensor.DS18B20, "01204e898f03")

# Print Sensor Info
    for sensor in W1ThermSensor.get_available_sensors():
      print("Sensor %s has temperature %.2f" % (sensor.id, sensor.get_temperature()))
#    print ("Humidity is ", humidity)
#    print ("Temperature is ", envTemperature)

    # display with hardware SPI:
    ''' Warning!!!Don't  create multiple display objects!!! '''
    #disp = LCD_2inch.LCD_2inch(spi=SPI.SpiDev(bus, device),spi_freq=10000000,rst=RST,dc=DC,bl=BL)
    disp = LCD_2inch.LCD_2inch()
    # Initialize library.
    disp.Init()
    # Clear display.
    disp.clear()

    # Create blank image for drawing.
    image = Image.new("RGB", (disp.height, disp.width ), "blue")
    draw = ImageDraw.Draw(image)
    font40 = ImageFont.truetype("../Font/Font02.ttf", 40)
    font30 = ImageFont.truetype("../Font/Font02.ttf", 30)
    font25 = ImageFont.truetype("../Font/Font02.ttf", 25)
    font20 = ImageFont.truetype("../Font/Font02.ttf", 20)
    font15 = ImageFont.truetype("../Font/Font02.ttf", 15)

    #Create Image Frame 
    def imageFrame ():
     draw.line([(7,7),(313,7)], fill = "white",width = 4)
     draw.line([(7,7),(7,233)], fill = "white",width = 4)
     draw.line([(7,233),(313,233)], fill = "white",width = 4)
     draw.line([(313,7),(313,233)], fill = "white",width = 4)
     #draw.rectangle([(30,20),(290,60)],fill = "BLUE")
     draw.text((200,210), 'Carimali Pratica', font = font15, fill = "white")
     #draw.text((50, 20), 'Group 1 Temperature: ', font = font20, fill = "BLUE")
     #draw.polygon(((30, 50), (70, 35), (70, 65)), fill="green")
     #draw.rectangle([(70,40),(100,60)],fill = "GREEN")
     #draw.text((50, 85), 'Group 2 Temperature: ', font = font20, fill = "BLUE")
#     image=image.rotate(180)
     disp.ShowImage(image)

    #Get Temperature Readings and display time
    def getTemperatureReadings ():
# Set up a switch so that only 1 sensor is read each time to reduce the delay
     b = True
#     temperature2 = round(sensor2.get_temperature(), 1)
     while True:
       # Get the weight. 
       val = round(hx.get_weight(5),1)
       #print(val)
  
       if b == True:
        temperature1 = round(sensor1.get_temperature(), 1)
        b = False
       else:
        time.sleep(0.6)
        b = True
       if temperature1 < 87:
         draw.ellipse((50,85,70,105), fill = "red")
       else:  
         draw.ellipse((50,85,70,105), fill = "blue")  
#       if temperature2 < 87:
#         draw.ellipse((250,85,270,105), fill = "red")
#       else:  
#         draw.ellipse((250,85,270,105), fill = "blue")  
       draw.rectangle([(25,35),(115,75)],fill = "blue")
       draw.rectangle([(220,35),(300,75)],fill = "blue")
       draw.text((25, 35), str(temperature1), font = font40, fill = "white")
       draw.rectangle([(85,100),(175,140)],fill = "blue")
       draw.text((85,100), str(val), font=font40, fill = "white")
       #draw.text((85,100), datetime.datetime.now().strftime('%S'), font=font40, fill = "white")
#       draw.text((220, 35), str(temperature2), font = font40, fill = "white")
       draw.rectangle([(15,210),(150,226)],fill = "blue")
       draw.text((15,210), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), font=font15, fill = "white")
       disp.ShowImage(image)
#       time.sleep(0.2)

#   Display Temperature Readings and the Image Frame
    imageFrame()
    getTemperatureReadings()


except KeyboardInterrupt:
    disp.module_exit()
    logging.info("quit:")
    exit()
