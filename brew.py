#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
import os
import Adafruit_ADS1x15
import sys
import sqlalchemy as db

from flowMeter import flowCount, writeCommand


# constants used later
adc = Adafruit_ADS1x15.ADS1015()
GAIN = 8
num = 0
heatPointLow = 750
heatPointHigh = 1000


# initialize GPIO

GPIO.setmode(GPIO.BCM)
outPinList = [17, 9, 27, 22, 10]
# 17 -water pump
# 9  -air pump
# 27 -water solenoid
# 22 -heat
# 10 -vent
inPinList = [26, 19, 13, 6]
# 26 -low
# 19 -med
# 13 -high
# 6 -overflow

for i in outPinList:
	GPIO.setup(i, GPIO.OUT)
	GPIO.output(i, GPIO.LOW)

for i in inPinList:
	GPIO.setup(i, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#database setup

engine = db.create_engine('sqlite:///beanapi.db')

class coilModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	state = db.Column(db.Integer, nullable=False)


# the land of functions

def emptyReservoir(a):
# takes 'a' time in seconds to run the air pump to drain the tank
	GPIO.output(9, GPIO.HIGH)
	b = 0
	while b < a:
		b = b + 1
		time.sleep(1)
	GPIO.output(9, GPIO.LOW)

def coffeeHeat(level):
# this controls the heat cycle when brewing
	n = os.fork()
	if n == 0:
		#child process fills and then dies. requires level as low med high
		fillWhileHeat(level)
	h = 5 # this is how many seconds the temp must hold otherwise heat again
	getTemp()
	a = getTemp()
	while (a > heatPointLow): # we need to let the sensor normalize to cold water being added
		a = getTemp()
		time.sleep(0.1)
	a = getTemp()
	maxa = 0
	offset = a + h
	offsetTotal = heatPointHigh - a
	offsetHighA = heatPointHigh - offset
	b = 0
	while (b <= h):
		while( a < heatPointHigh ):
			b = 0
			GPIO.output(22, GPIO.HIGH)
			a = getTemp()
			offsetA = a - offset
			maxa = (offsetA if offsetA > maxa else maxa)
			maxa = (offsetHighA if offsetA > offsetHighA else maxa)
			time.sleep(0.1)
		GPIO.output(22, GPIO.LOW)
		b = b + 1
		time.sleep(1)
		a = getTemp()
		offsetA = a - offset
		maxa = (offsetA if offsetA > maxa else offsetA) # this is pointless
		maxa = (offsetHighA if offsetA > offsetHighA else maxa)
		time.sleep(0.1)
		c = maxa + b
	for x in [10, 22]:
		GPIO.output(x, GPIO.LOW)

def fillWhileHeat(a):
# fill the reservoir to specified level of 'low', 'med, 'high' and return the total flow count
	if a == 'low':
		lvl = 26
		#flowMax = 21000
	elif a == 'med':
		lvl = 19
		#flowMax = 28000
	elif a == 'high':
		lvl = 13
		#flowMax = 32000
	else:
		#print ("the function fillWhileHeat requires a level as 'low', 'med', 'high'")
		return None
	num = 0
	b = 0
	while (getTemp() < 300):
		time.sleep(1)
	writeCommand(1)
	#print ('flow counter cleared')
	for x in [17, 27, 10]:
		GPIO.output(x, GPIO.HIGH)
	for x in [26, 19, 13]:
		GPIO.setup(x, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	while GPIO.input(lvl):
		time.sleep(1)
		b = flowCount()
		num = num + 1
	for x in [17, 27]:
		GPIO.output(x, GPIO.LOW)
	with open("fillcount-%s.txt" % (a), "a+") as fl:
		fl.write(str(b) + "\n")
	sys.exit()

def getTemp():
	l = [0] * 10
	c = 0
	while c < 10:
		l.insert(0, i2cadc())
		l.pop()
		c = c + 1
	return average(l)

def average(lst):
	return sum(lst) / len(lst)

def i2cadc():
	i = ''
	while i == '':
		try:
			i = adc.read_adc(0, gain=GAIN)
		except:
			i = ''
	return i

def brewCoffee():
# used to dispense one french press worth of water had coffee brewing temperature
	coffeeHeat('high')
	emptyReservoir(20)
	coffeeHeat('high')
	emptyReservoir(20)
	coffeeHeat('high')
	emptyReservoir(20)


brewCoffee()

GPIO.cleanup()
dbupdate('active', 0)