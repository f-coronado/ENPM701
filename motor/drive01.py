import RPi.GPIO as gpio
import numpy as np
import time
import cv2 as cv

# define pin allocations
trig = 16
echo = 18

# setup GPIO board and pins
gpio.setmode(gpio.BOARD)
gpio.setup(trig, gpio.OUT)
gpio.setup(echo, gpio.IN)

gpio.setup(31, gpio.OUT) # IN1
gpio.setup(33, gpio.OUT) # IN2
gpio.setup(35, gpio.OUT) # IN3
gpio.setup(37, gpio.OUT) # IN4


# setup gpio pins and set pin 36 as output
#gpio.setmode(gpio.BOARD)
gpio.setup(36, gpio.OUT) # setup gripper pin to be output
pwm = gpio.PWM(36, 50) # initialize pwm to be 50 Hz
pwm.start(7.5) # start PWM frequency to 5% duty cycle


# initialize camera
cap = cv.VideoCapture(0)
if not cap.isOpened():
        print("couldn't open camera")
        exit()

# define video properties
video_file = "motor01.mp4"
fps = 1
fourcc = cv.VideoWriter_fourcc(*'XVID')
out = cv.VideoWriter('motor01.mp4', fourcc, fps, (int(cap.get(3)), int(cap.get(4))))

min_cycle = 3
max_cycle = 9


def distance():

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

#	gpio.cleanup()

	return distance

def init():

        gpio.setmode(gpio.BOARD)
        gpio.setup(31, gpio.OUT) # IN1
        gpio.setup(33, gpio.OUT) # IN2
        gpio.setup(35, gpio.OUT) # IN3
        gpio.setup(37, gpio.OUT) # IN4


def forward(tf):
#        init()

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
#        gpio.cleanup()


def reverse(tf):
#        init()

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
#        gpio.cleanup()


def pivotleft(tf):
#        init()

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
#        gpio.cleanup()


def pivotright(tf):
#        init()

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
#        gpio.cleanup()


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
	print("setting duty cycle to: ", duty_cycle)
	time.sleep(1)

def grab(duration):

        for cycle in duty_list:
                print("cycle is: ", cycle)
                set_cycle(cycle)
                write_on_frame(cycle)
                time.sleep(duration)
                print("sleeping...")

        create_video()
        pwm.stop()
        gpio.cleanup()


def key_input(event):
	init()
	print("key: ", event)
	key_press = event
	tf = 1

	if key_press == 'f':
		print("entered 'f'")
		forward(tf)
	elif key_press == 'b':
		print("entered 'b'")
		reverse(tf)
	elif key_press == 'l':
		print("entered 'l'")
		pivotleft(tf)
	elif key_press == 'r':
		print("entered 'r'")
		pivotright(tf)
	elif 3 <= key_press <= 9:
		print("entered number: ", key_press)
		set_cycle(key_press)
	else:
		print("invalid key pressed")

print("enter 'p' at any time to exit script")
while True:
	pwm.start(8)
	time.sleep(1)
	key_press = input("select driving mode: ")
	duty_cycle = float(input("select duty cycle for servo between 3-9: "))

	if key_press == 'p':
		break
	key_input(key_press)
	key_input(duty_cycle)
	print("distance: ", distance(), " cm\n")

pwm.stop()
gpio.cleanup
