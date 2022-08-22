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
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    print("Bye!")
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
     draw.text((200,210), 'Expobar', font = font15, fill = "white")
    # Rotate image if needed
    # image=image.rotate(180)
     disp.ShowImage(image)
    
    #Get Temperature Readings and display time
    async def getTemperatureReadings ():
     # Get the first temperature and weight readings
     temperature1 = round(await sensor1.get_temperature(), 1)
     val = round(hx.get_weight(5),1)
     # There is no async for HX711, so we create a swtich
     # to read only one sensor at a time, either temperature or weight, to avoid delay
     b = True
     # Create an array for weight readings
     weights = [0,0,0]
     #Main loop
     while True:
       # Get the weight. 
       val = round(hx.get_weight(5),1)
       # add the last weight to the array and check if the last 3 values are more or less the same
       #if so, tare the scales
       weights.append(val)
       if len(weights) > 3:
        del weights[0]
       if math.fabs(weights[2] - weights[1]) < 2 and math.fabs(weights[2] - weights[1]) < 2:
        hx.tare()
  
#       if b == True:
        #await readTempeature()
       temperature1 = round(await sensor1.get_temperature(), 1)
       print (temperature1)
#        b = False
#       else:
#        await asyncio.sleep(0.6)
#        b = True
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
    await getTemperatureReadings()


 except KeyboardInterrupt:
    disp.module_exit()
    logging.info("quit:")
    exit()
asyncio.run(main())