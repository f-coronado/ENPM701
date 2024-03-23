import RPi.GPIO as gpio
import numpy as np
import time

def init():
	gpio.setmode(gpio.BOARD)
	gpio.setup(31, gpio.OUT) # IN1
	gpio.setup(33, gpio.OUT) # IN2
	gpio.setup(35, gpio.OUT) # IN3
	gpio.setup(37, gpio.OUT) # IN4

def gameover():
	# set all pins low
	gpio.output(31, False)
	gpio.output(33, False)
	gpio.output(35, False)
	gpio.output(37, False)

def forward(tf):
	init()

	# left wheels
	gpio.output(31, True)
	gpio.output(33, False)

	# right wheels
	gpio.output(35, False)
	gpio.output(37, True)

	# wait
	time.sleep(tf)
	# send all pins low and cleanup
	gameover()
	gpio.cleanup()


def reverse(tf):
	init()

	# left wheels
	gpio.output(31, False)
	gpio.output(33, True)

	# right wheels
	gpio.output(35, True)
	gpio.output(37, False)

	# wait
	time.sleep(tf)
	# send all pins low and cleanup
	gameover()
	gpio.cleanup()



def pivotleft(tf):
	init()

	# left wheels
	gpio.output(31, True)
	gpio.output(33, False)

	# right wheels
	gpio.output(35, True)
	gpio.output(37, False)

	# wait
	time.sleep(tf)
	# send all pins low and cleanup
	gameover()
	gpio.cleanup()



def pivotright(tf):
	init()

	# left wheels
	gpio.output(31, False)
	gpio.output(33, True)

	# right wheels
	gpio.output(35, False)
	gpio.output(37, True)

	# wait
	time.sleep(tf)
	# send all pins low and cleanup
	gameover()
	gpio.cleanup()

def key_input(event):
        init()
        print("key: ", event)
        key_press = event
        tf = 1

        if key_press.lower() == 'f':
                forward(tf)
        elif key_press.lower() == 'b':
                reverse(tf)
        elif key_press.lower() == 'l':
                pivotleft(tf)
        elif key_press.lower() == 'r':
                pivotright(tf)
        else:
                print("invalid key pressed")

while True:
        time.sleep(1)
#        print("distance: ", distance(), " cm")
        key_press = input("select driving mode: ")
        if key_press == 'p':
                break
        key_input(key_press)


#forward(1)
#reverse(1)
#pivotleft(2)
#pivotright(2)
