import RPi.GPIO as gpio
import numpy as np
import time
import cv2 as cv

# setup gpio pins and set pin 36 as output 
gpio.setmode(gpio.BOARD)
gpio.setup(36, gpio.OUT)
pwm = gpio.PWM(36, 50)
#pwm.start(5) # start PWM frequency to 5% duty cycle

# initialize camera
cap = cv.VideoCapture(0)
if not cap.isOpened():
        print("couldn't open camera")
        exit()

# define video properties
video_file = "dutyCycle.mp4"
fps = 1
fourcc = cv.VideoWriter_fourcc(*'XVID')
out = cv.VideoWriter('dutyCycle.mp4', fourcc, fps, (int(cap.get(3)), int(cap.get(4))))

min_cycle = 3
max_cycle = 9


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
	gpio.output(trig, True)
	time.sleep(0.00001)
	gpio.output(trig, False)

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

def init():

        gpio.setmode(gpio.BOARD)
        gpio.setup(31, gpio.OUT) # IN1
        gpio.setup(33, gpio.OUT) # IN2
        gpio.setup(35, gpio.OUT) # IN3
        gpio.setup(37, gpio.OUT) # IN4


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


def gameover():
        # set all pins low
        gpio.output(31, False)
        gpio.output(33, False)
        gpio.output(35, False)
        gpio.output(37, False)


def set_cycle(duty_cycle):
	max_cycle = 9
	if duty_cycle > max_cycle:
		duty_cycle = max_cycle
	pwm.ChangeDutyCycle(duty_cycle)
	#print("setting duty cycle to: ", duty_cycle)
	time.sleep(5)


def grab(duration):

	pwm.start(min_cycle)
	for duty_cycle in range(min_cycle, max_cycle + 1):
	        set_cycle(duty_cycle)
	        time.sleep(duration)
	for duty_cycle in range(max_cycle - 1, min_cycle - 1, -1):
	        set_cycle(duty_cycle)
	        time.sleep(duration)


def key_input(event):
	init()
	print("key: ", event)
	key_press = event
	tf = 1

	if key_press == 'f':
		forward(tf)
	elif key_press == 'b':
		reverse(tf)
	elif key_press == 'l':
		pivotleft(tf)
	elif key_press == 'r':
		pivotright(tf)
	elif 3 <= key_press <= 9:
		set_cycle(key_press)
	else:
		print("invalid key pressed")

while True:
	time.sleep(1)
	print("distance: ", distance(), " cm")
	key_press = input("select driving mode: ")
	duty_cycle = int(input("select duty cycle for servo between 3-9: "))
	
	if key_press == 'p':
		break
	key_input(key_press)
	key_input(duty_cycle)
