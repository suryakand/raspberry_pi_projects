# 
# Home_Weather_Display.py
#

from grovepi import *
from grove_rgb_lcd import *
from time import sleep
from math import isnan

import datetime
from pyHS100 import SmartPlug
from pprint import pformat as pf

import csv

import requests 
import json

SLEEP_INTERVAL = 600 #seconds
humidity_threshold_low=50
humidity_threshold_high=58
humidity_range = range(humidity_threshold_low, humidity_threshold_high)

plug_ip= "192.168.0.13"
plug = SmartPlug(plug_ip)
plug.turn_off() #Trun off plug when monitoring statrs

dht_sensor_port = 7 # connect the DHT sensor to port 7
dht_sensor_type = 0 # use 0 for the blue-colored sensor and 1 for the white-colored sensor

# set green as backlight color
# we need to do it just once
# setting the backlight color once reduces the amount of data transfer over the I2C line
setRGB(0,255,0)

# API_SERVER = 'http://192.168.0.22:5000'
API_SERVER = 'https://rpi-home-weather-station.herokuapp.com'
API_ENDPOINT_HUMIDITY = API_SERVER + '/humidity'
API_ENDPOINT_TEMPRATURE = API_SERVER + '/temprature'

def postData(API_ENDPOINT, data):
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	try:
		# sending post request and saving response as response object 
		r = requests.post(url = API_ENDPOINT, data = json.dumps(data), headers=headers) 
		# extracting response text  
		# print(r.text) 
	except:
		print('Error calling API {}'.format(API_ENDPOINT))
		
while True:
	try:
        # get the temperature and Humidity from the DHT sensor
		[ temp,hum ] = dht(dht_sensor_port,dht_sensor_type)
		now = datetime.datetime.now()
		postData(API_ENDPOINT_HUMIDITY, {"humidity": hum})
		postData(API_ENDPOINT_TEMPRATURE, {"temprature": temp})
		
		print("temp =", temp, "thumidity =", hum,"% ", now)
		
		line = [now, temp, hum]
		with open('./home_temp_humidity.csv', 'a') as writeFile:
			writer = csv.writer(writeFile)
			writer.writerow(line)
			writeFile.close()

		if((hum in humidity_range or hum < humidity_threshold_low) and plug.state != "ON"):
			plug.turn_on()
			print("Turning ON Humidifire")
			
		if(hum >= humidity_threshold_high and plug.state != "OFF"):
			plug.turn_off()
			print("Turning OFF Humidifire")	
				
		# check if we have nans
		# if so, then raise a type error exception
		if isnan(temp) is True or isnan(hum) is True:
			raise TypeError('nan error')

		t = str(temp)
		h = str(hum)

        # instead of inserting a bunch of whitespace, we can just insert a \n
        # we're ensuring that if we get some strange strings on one line, the 2nd one won't be affected
		setText_norefresh("Temp:" + t + "C\n" + "Humidity :" + h + "%")

	except (IOError, TypeError) as e:
		print(str(e))
		# and since we got a type error
		# then reset the LCD's text
		setText("")

	except KeyboardInterrupt as e:
		print(str(e))
		# since we're exiting the program
		# it's better to leave the LCD with a blank text
		setText("")
		break

	# wait some time before re-updating the LCD
	sleep(SLEEP_INTERVAL)


