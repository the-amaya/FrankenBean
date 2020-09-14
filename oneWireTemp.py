#!/usr/bin/python
import RPi.GPIO as GPIO
import glob
import time

GPIO.setmode(GPIO.BCM)

# initialized pins

outtemp = '/sys/bus/w1/devices/28-000004a83011/w1_slave'
intemp = '/sys/bus/w1/devices/28-000004a7915b/w1_slave' 

# loop through pins and set GPIOs accordingly

for i in pinList:
	GPIO.setup(i, GPIO.OUT)
	GPIO.output(i, GPIO.HIGH)

# sleep between turning on in the main loop

def readTempRaw(device):
	# 1wire direct read function used by read_temp()
	f = open(device, 'r')
	lines = f.readlines()
	f.close()
	return lines

def readTemp(device):
# returns a tuple [tempC, tempF] for specified 1wire device
# attempts to re-read the sensor over and over until good data is received. this is not safe and will hang if unable to ever read good data
	lines = readTempRaw(device)
	while (lines[0].strip()[-3:] != 'YES' or lines[1].find('t=') == -1):
		time.sleep(0.2)
		lines = readTempRaw()
	equals_pos = lines[1].find('t=')
	temp_string = lines[1][equals_pos+2:]
	temp_c = float(temp_string) / 1000.0
	temp_f = temp_c * 9.0 / 5.0 + 32.0
	return temp_c, temp_f


a = 1
while True:
	while a < 10:
		a = a + 1
		print '%s%f%s%f'%('intemp ', readTemp(intemp)[1], '    outtemp ', readTemp(outtemp)[1])
		time.sleep(.5)
	a = 1
	print time.strftime('%l:%M%p %Z on %b %d, %Y')
