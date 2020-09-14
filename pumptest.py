#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
import os
import Adafruit_ADS1x15

from flowMeter import flowCount, writeCommand
from oneWireTemp import readTemp


# constants used later
adc = Adafruit_ADS1x15.ADS1015()
GAIN = 8
num = 0
temp1 = '/sys/bus/w1/devices/28-000004a83011/w1_slave'
temp2 = '/sys/bus/w1/devices/28-000004a7915b/w1_slave' 


# initialize GPIO

GPIO.setmode(GPIO.BCM)
outPinList = [17, 18, 27, 22, 23, 24, 25, 10]
inPinList = [5, 26, 19, 13, 14]

for i in outPinList:
	GPIO.setup(i, GPIO.OUT)
	GPIO.output(i, GPIO.HIGH)

for i in inPinList:
	GPIO.setup(i, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


# the land of functions

def brewWatch(min):
# takes a value in minutes to monitor the coffee temp probe and return the average temp
	a = min * 60
	l = []
	c = 0
	while int(c) < int(a):
		c = c + 1
		l.insert(0, readTemp(a)[1])
		print ('count %i of %i   current average = %f' % (c, a, average(l)))
		time.sleep(1)
	return average(l)

def maxTemp(a):
# takes one temperature reading per second for 'a' seconds then returns the maximum temp recorded during that time
	l = [0] * a
	c = 0
	while c < a:
		c = c + 1
		l.insert(0, readTemp(a)[1])
		l.pop()
		print ('count %i of %i   current max read = %f' % (c, a, max(l)))
		time.sleep(1)
	return max(l)

def emptyReservoir(a):
# takes 'a' time in seconds to run the air pump to drain the tank
	GPIO.output(10, GPIO.LOW)
	print ("Running the air pump for %i seconds" % (a))
	time.sleep(a)
	GPIO.output(10, GPIO.HIGH)
	print ("Air pump now off")


def fillReservoir(a):
# fill the reservoir to specified level of 'low', 'med, 'high' and return the total flow count
	if a == 'low':
		lvl = 26
	elif a == 'med':
		lvl = 19
	elif a == 'high':
		lvl = 13
	else:
		print ("the function fillReservoir now requires a level as 'low', 'med', 'high'")
		return None
	num = 0
	writeCommand('clear')
	print ('flow counter cleared')
	for x in [17, 18, 22]:
		GPIO.output(x, GPIO.LOW)
	print ("Pump and Solenoids On")
	for x in [26, 19, 13]:
		GPIO.setup(x, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	while GPIO.input(lvl):
		print ('Secs:%d, Target level: %d, Low:%d, Med:%d, High:%d, current flow count:%d ' % (num, lvl, GPIO.input(26), GPIO.input(19), GPIO.input(13), flowOut()))
		num = num + 1
		time.sleep(1)
	GPIO.output(17, GPIO.HIGH)
	GPIO.output(18, GPIO.HIGH)
	GPIO.output(22, GPIO.HIGH)
	print ('pump and solenoids off')
	return flowOut()

def heater(a):
# heats to the target raw sensor value
# 950 seems to be good for coffee as of this revision
	print ('heating')
	GPIO.output(22, GPIO.LOW)
	GPIO.output(27, GPIO.LOW)
	heat = getTemp()
	while heat < a:
		print (heat)
		heat = getTemp()
		time.sleep(1)
	GPIO.output(27, GPIO.HIGH)
	GPIO.output(22, GPIO.HIGH)
	print ('heating complete')

def coffeeHeat():
# this controls the heat cycle when brewing
	getTemp()
	a = getTemp()
	while (a > 700): # we need to let the sensor normalize to cold water being added
		a = getTemp()
		print (a)
		time.sleep(0.1)
	GPIO.output(22, GPIO.LOW)
	GPIO.output(27, GPIO.LOW)
	a = getTemp()
	while( a < 950 ): # heat to serving temp -raw sensor reading- this may need to go into a constant up top for easy adjustment
		a = getTemp()
		time.sleep(0.1)
		print (a)
	GPIO.output(27, GPIO.HIGH)
	GPIO.output(22, GPIO.HIGH)

def stepTest(a):
# takes a list of numbers then runs one heat/dispense cycle and records the maximum output temperature
# used for diagnostics to calibrate dispensing temperature
	for i in a:
		i = int(i)
		fillReservoir('high')
		time.sleep(10)
		heater(i)
		emptyReservoir(20)
		j = maxTemp(temp1)
		f = ('for sensor value %i the max output temp was %f' % (i, j))
		print (f)
		with open("steptest.txt", "a+") as att_file:
			att_file.write(f + "\n")
		print ('sleeping for 10 seconds to let temps settle')
		time.sleep(10)

def getTemp():
	l = [0] * 10
	c = 0
	while c < 10:
		l.insert(0, i2cadc())
		l.pop()
		print (*l, average(l))
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
	dc = fillReservoir('med')
	brewCoffee()
	emptyReservoir(18)
	dc = dc + fillReservoir('med')
	brewCoffee()
	emptyReservoir(18)
	dc = dc + fillReservoir('low')
	brewCoffee()
	emptyReservoir(14)
	dc = dc + fillReservoir('low')
	brewCoffee()
	emptyReservoir(14)
	print ("total dispensed liquid = %i" % dc)
	print ("enjoy your coffee bitch")


try:
	while True:
		#os.system('clear')
		print ('Please use the following commands (do not include parenthesies in your commands)')
		print ('')
		print ('*** diagnostic options ***')
		print ('')
		print ('    fill (low, med, high)')
		print ('    drain (time in seconds) #20 seconds should completely empty the tank')
		print ('    heat (target sensor value to heat to)')
		print ('    cycle (number) # will run provided number of progressive low/med/high fill-drain cycles')
		print ('    step (two or more numbers) # step test to heat and log dispensed water temp')
		print ('')
		print ('*** this is where the magic happens ***')
		print ('')
		print ('    brew # brew a french press of coffee')
		print ('')
		print ('###')

		usrip = input()

		if (usrip[:4] == 'fill'): # this should silently fail safe
			if usrip[5:] in {'low', 'med', 'high'}
				fillReservoir(usrip[5:])
			
		elif (usrip[:4] == 'heat'): # the int here should catch bad input (though we will crash to terminal at the moment)
			print ('target temp %s' % usrip[5:])
			heater(int(usrip[5:]))
			
		elif (usrip[:5] == 'drain'): # the int here should catch bad input (though we will crash to terminal at the moment)
			emptyReservoir(int(usrip[6:]))
			
		elif (usrip[:5] == 'cycle'): # the int here should catch bad input (though we will crash to terminal at the moment)
			fdc = int(usrip[6:])
			while fdc > 0:
				fdc = fdc - 1
				for a in ['low', 'med', 'high']:
					fillReservoir(a)
					emptyReservoir(20)

		elif (usrip == '10'): # undocumented - verifies we are able to read the temp sensor
			sd = 0
			while sd < 10:
				sd = sd + 1
				print (getTemp())
				time.sleep(1)
			time.sleep(5)

		elif (usrip[:4] == 'step'): # we should catch bad user input later with an int() but this needs input sanitization here at some point
			usrlst = usrip[5:].split()
			stepTest(usrlst)

		elif (usrip[:5] == 'watch'): # undocuments because the function still needs work
			brewWatch(usrip[6:])

		elif (usrip == 'brew'):
			brewCoffee()

		else:
			print ("You need to say high, med, or low...Jackass....")


except KeyboardInterrupt:
	print ("Quit")
	GPIO.cleanup()
	print ("Turning Shit Off Real Quick...")

print ('EoF CLEANUP ROUTINE')
GPIO.cleanup()
