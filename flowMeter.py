#!/usr/bin/python3
import smbus
import time

bus = smbus.SMBus(1)
address = 0x04

# for some reason this only works when the functions live in their own file... no idea why
# functions intended for use: writeCommand(), flowCount().

def writeCommand(val):
# this writes a command to the i2c bus address specified above
# an input value of '1' will reset the counter
	try:
		bus.write_byte(address, val)
		print ('flowcounter reset')
	except:
		print ('failed to reset flow counter')
		pass

def readTotal():
# this function will attempt to read the current flow count total value from the address specified above
# this function will continue to re-try on failure to infinity. this should be resolved either in this function or in items using this function
	a = None
	while a is None:
		try:
			a = bus.read_word_data(address, 0)
		except:
			print ('readTotal() re-read')
			a = None
	return a

def flowCount():
# when called as flowCount() will return reliable flow count
	a = ''
	while ( a == '' ):
		l = []
		k = []
		for i in range(0, 3):
			l.insert(i, readTotal())
			time.sleep(0.1)
		k.append(abs(l[0] - l[1]))
		k.append(abs(l[1] - l[2]))
		k.append(abs(l[2] - l[0]))
		a = '1'
		if (2000 < sum(k)):
			print (l)
			print (k)
			print (sum(k))
			print ('difference in flow readings. assuming possible bad read')
			a = ''
	return average(l)

def average(lst):
	return sum(lst) / len(lst)
