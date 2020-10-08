#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
import os
import Adafruit_ADS1x15
import sys

from flowMeter import flowCount, writeCommand
from oneWireTemp import readTemp
from progressBar import printProgressBar

# constants used later
adc = Adafruit_ADS1x15.ADS1015()
GAIN = 8
num = 0
temp1 = '/sys/bus/w1/devices/28-000004a83011/w1_slave'
temp2 = '/sys/bus/w1/devices/28-000004a7915b/w1_slave'
heatPointLow = 850
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
	GPIO.output(10, GPIO.HIGH)
	b = 0
	#print ("Running the air pump for %i seconds" % (a))
	printProgressBar(0, a, prefix = 'Drain Progress:  ', suffix = 'Complete', length = 100)
	while b < a:
		b = b + 1
		time.sleep(1)
		printProgressBar(b, a, prefix = 'Drain Progress:  ', suffix = 'Complete', length = 100)
	printProgressBar(a, a, prefix = 'Drain Progress:  ', suffix = 'Complete', length = 100)
	print()
	GPIO.output(10, GPIO.LOW)
	#print ("Air pump now off")


def fillReservoir(a):
# fill the reservoir to specified level of 'low', 'med, 'high' and return the total flow count
	if a == 'low':
		lvl = 26
		flowMax = 21000
	elif a == 'med':
		lvl = 19
		flowMax = 28000
	elif a == 'high':
		lvl = 13
		flowMax = 32000
	else:
		print ("the function fillReservoir now requires a level as 'low', 'med', 'high'")
		return None
	num = 0
	writeCommand(1)
	#print ('flow counter cleared')
	for x in [10, 27, 17]:
		GPIO.output(x, GPIO.HIGH)
	printProgressBar(0, flowMax, prefix = 'Fill Progress:   ', suffix = 'Complete', length = 100)
	while GPIO.input(lvl):
		time.sleep(1)
		b = flowCount()
		flowSafe = (b if b < flowMax else flowMax)
		#print ('Secs:%d, Target level: %d, Low:%d, Med:%d, High:%d, current flow count:%d ' % (num, lvl, GPIO.input(26), GPIO.input(19), GPIO.input(13), flowCount()))
		printProgressBar(flowSafe, flowMax, prefix = 'Fill Progress:   ', suffix = 'Complete', length = 100)
		num = num + 1
	printProgressBar(flowMax, flowMax, prefix = 'Fill Progress:   ', suffix = 'Complete', length = 100)
	print()
	for x in [10,27,17]:
		GPIO.output(x, GPIO.LOW)
	with open("fillcount-%s.txt" % (a), "a+") as fl:
		fl.write(str(b) + "\n")
	return b

def heater(a):
# heats to the target raw sensor value
# 950 seems to be good for coffee as of this revision
	print ('heating')
	GPIO.output(22, GPIO.HIGH)
	GPIO.output(27, GPIO.HIGH)
	heat = getTemp()
	while heat < a:
		print (heat)
		heat = getTemp()
		time.sleep(1)
	GPIO.output(27, GPIO.LOW)
	GPIO.output(22, GPIO.LOW)
	print ('heating complete')

def coffeeHeat(level):
# this controls the heat cycle when brewing
	n = os.fork()
	if n == 0:
		#child process fills and then dies. requires level as low med high
		fillWhileHeat(level)
	h = 5 # this is how many seconds the temp must hold otherwise heat again
	getTemp()
	a = getTemp()
	GPIO.output(22, GPIO.HIGH) #heater
	while (a > heatPointLow): # we need to let the sensor normalize to cold water being added
		a = getTemp()
		#print (a)
		time.sleep(0.1)
	a = getTemp()
	maxa = 0
	offset = a + h
	offsetTotal = heatPointHigh - a
	offsetHighA = heatPointHigh - offset
	printProgressBar(0, offsetTotal, prefix = 'Heating progress:', suffix = 'Complete', length = 100)
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
			printProgressBar((maxa), offsetTotal, prefix = 'Heating progress:', suffix = 'Complete', length = 100)
		GPIO.output(22, GPIO.LOW)
		b = b + 1
		time.sleep(1)
		a = getTemp()
		offsetA = a - offset
		maxa = (offsetA if offsetA > maxa else offsetA) # this is pointless
		maxa = (offsetHighA if offsetA > offsetHighA else maxa)
		time.sleep(0.1)
		c = maxa + b
		printProgressBar((c), offsetTotal, prefix = 'Heating progress:', suffix = 'Complete', length = 100)
	printProgressBar(offsetTotal, offsetTotal, prefix = 'Heating progress:', suffix = 'Complete', length = 100)
	print()
	for x in [10, 22]
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
	#return b
	sys.exit()

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
		#print (*l, average(l))
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
	os.system('clear')
	print ('Cycle 1 of 3 starting')
	#dc = fillReservoir('med')
	coffeeHeat('high')
	emptyReservoir(20)
	print ('Cycle 2 of 3 starting')
	#dc = dc + fillReservoir('med')
	coffeeHeat('high')
	emptyReservoir(20)
	print ('Cycle 3 of 3 starting')
	#dc = dc + fillReservoir('low')
	coffeeHeat('high')
	emptyReservoir(20)
	#print ('Cycle 4 of 4 starting')
	#dc = dc + fillReservoir('low')
	#coffeeHeat()
	#emptyReservoir(14)
	#print ("total dispensed liquid = %i" % dc)
	print ("enjoy your coffee bitch")
	print ('')


try:
	os.system('clear')
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
			if usrip[5:] in ['low', 'med', 'high']:
				print(fillReservoir(usrip[5:]))

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

#print ('EoF CLEANUP ROUTINE')
#GPIO.cleanup()
