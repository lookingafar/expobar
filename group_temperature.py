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
import math
import asyncio
from lib import LCD_2inch
from PIL import Image,ImageDraw,ImageFont,ImageColor
from w1thermsensor import AsyncW1ThermSensor, Sensor

#HX711 stuff
EMULATE_HX711=False

referenceUnit = 464.078

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711

def cleanAndExit():

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    sys.exit()

hx = HX711(5, 6)

hx.set_reference_unit(referenceUnit)

hx.reset()

hx.tare()

# Raspberry Pi pin configuration:
RST = 27
DC = 25
BL = 18
bus = 0 
device = 0 
logging.basicConfig(level=logging.DEBUG)
async def main():
 try:

    #Initialize Temperature Sensors
    sensor1 = AsyncW1ThermSensor(Sensor.DS18B20, "3c0107d67cb6")

    # Initialize display with hardware SPI. Only one display variable should be used
    disp = LCD_2inch.LCD_2inch()
    # Initialize library.
    disp.Init()
    # Clear display.
    disp.clear()

    # Create blank image for drawing.
    image = Image.new("RGB", (disp.height, disp.width ), "#00BFFF")
    draw = ImageDraw.Draw(image)
    # Set font sizes
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
     draw.text((200,210), 'Expobar', font = font15, fill = "white")
    # Rotate image if needed
    # image=image.rotate(180)
     disp.ShowImage(image)
    
    # Get temperature readings function
    async def readTemperature ():
        temperature1 = round(await sensor1.get_temperature(), 1)
        return temperature1
    
    # Get weight readings function
    async def readWeight ():
        weight1 = round(hx.get_weight(), 1)
        return weight1
    
    #Main loop function
    async def getTemperatureReadings ():

     # Create an array for weight readings
     weights = [0,0,0]
     #Main loop
     while True:
       draw.rectangle([(25,35),(115,80)],fill = "#00BFFF")
       #draw.rectangle([(220,35),(300,80)],fill = "green")
       draw.text((25, 35), str(await readTemperature()), font = font40, fill = "white")
       draw.rectangle([(85,100),(205,145)],fill = "#00BFFF")
       draw.text((85,100), str(await readWeight()), font=font40, fill = "white")
       draw.rectangle([(15,210),(150,226)],fill = "#00BFFF")
       draw.text((15,210), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), font=font15, fill = "white")
       disp.ShowImage(image)

#   Display Temperature Readings and the Image Frame
    imageFrame()
    await getTemperatureReadings()


 except KeyboardInterrupt:
    disp.module_exit()
    cleanAndExit()
    logging.info("Keyboard interrupt:")
    exit()
 finally: 
    disp.module_exit()
    cleanAndExit()
    logging.info("quit:")
    exit()
asyncio.run(main())