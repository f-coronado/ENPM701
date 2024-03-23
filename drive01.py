import RPi.GPIO as gpio
import numpy as np
import time

def distance():
	
	# define pin allocations
	trig = 16
	echo = 18

	# setup GPIO board and pins
	gpio.setmode(gpio.BOARD)
	gpio.setup(trig, gpio.OUT)
	gpio.setup(echo, gpio.IN)

	# ensure output has no value
	gpio.output(trig, False)
	time.sleep(0.1)

	# generate trigger pulse
	gpio.output(Trig, True)
	time.sleep(0.00001)
	gpio.output(Trig, False)

	# generate echo time signal
	while gpio.input(echo) == 0:
		pulse_start = time.time()

	while gpio.input(echo) == 1:
		pulse_end = time.time()

	pulse_duration = pulse_end = pulse_start
	distance = pulse_duration * 17150 # convert time to distance
	distance = round(distance, 2)

	gpio.cleanup()

	return distance

def key_input(event):
	init()
	print("key: ", event)
	key_press = event
	tf = 1

	if key_press.lower() == 'w':
		forward(tf)
	elif key_press.lower() == 'r':
		reverse(tf)
	elif key_press.lower() == 'a':
		pivotleft(tf)
	elif key_press.lower() == 'r':
		pivotright(tf)
	else:
		print("invalid key pressed")

while True:
	time.sleep(1)
	print("distance: ", distance(), " cm")
	key_press = input("select driving mode: ")
	if key_press == 'p':
		break
	key_input(key_press)
