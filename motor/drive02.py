import RPi.GPIO as gpio
import time
import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv

## initialize gpio pins ##

def init():

	gpio.setmode(gpio.BOARD)
	gpio.setup(31, gpio.OUT) # IN1
	gpio.setup(33, gpio.OUT) # IN2
	gpio.setup(35, gpio.OUT) # IN3
	gpio.setup(37, gpio.OUT) # IN4

	gpio.setup(12, gpio.IN, pull_up_down = gpio.PUD_UP)
	gpio.setup(7, gpio.IN, pull_up_down = gpio.PUD_UP)


def gameover():

	gpio.output(31, False)
	gpio.output(33, False)
	gpio.output(35, False)
	gpio.output(37, False)

	gpio.cleanup()

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


def get_distance():

	distance = float(input("enter how long you want the robot to drive in meters(<1m):"))

	return round(distance, 4)

def get_tick_cnt(dist):

	ticks = (dist * 120 * 8)/.2048

	return ticks 


## main code ##
init()
counterFL = np.uint64(0)
counterBR = np.uint64(0)

buttonFL = int(0)
buttonBR = int(0)

# hw7
travel_distance = get_distance()
print("distance to travel is: ", travel_distance)
travel_ticks = get_tick_cnt(travel_distance)
print(travel_ticks, "ticks are needed to travel ", travel_distance, "m")


cap = cv.VideoCapture(0)
if not cap.isOpened():
       	print("could not open camera")
       	exit()

ret, frame = cap.read()
frame = cv.flip(frame, 1)
if not ret:
        print("could not capture frame")
        exit()

frame = cv.line(frame, (int(frame.shape[1]/2), 0), (int(frame.shape[1]/2), frame.shape[0]), (0, 255, 0), 1)

# independent motor control via pwm
pwmBL = gpio.PWM(31, 50)
pwmFR = gpio.PWM(37, 50)
val = 22
pwmBL.start(val)
pwmFR.start(val)
time.sleep(0.1)

BR_y = []
FL_y = []
BR_counter = []
FL_counter = []

with open('encodercontrol04.txt', 'w') as file: # open this file in write mode
	file.write("BRcnt  BR GPIO  FLcnt  FLGPIO\n") 

	for i in range(0, 100000):
		print("i: ", i)
		print("counterBR: ", counterBR, "counterFL: ", counterFL, "BR state: ", gpio.input(12), "FL state: ", gpio.input(7))
		file.write(f"{counterBR}\t{gpio.input(12)}\t{counterFL}\t{gpio.input(7)}\n") # write to the file

		if int(gpio.input(12)) != int(buttonBR):
			buttonBR = int(gpio.input(12))
			BR_y.append(gpio.input(12))
			counterBR += 1
			BR_counter.append(counterBR)

		if int(gpio.input(7)) != int(buttonFL):
			buttonFL = int(gpio.input(7))
			FL_y.append(gpio.input(7))
			counterFL += 1
			FL_counter.append(counterFL)

		if counterFL >= travel_ticks:
			pwmBL.stop()
			print("stopping FL")

		if counterBR >= travel_ticks:
			pwmFR.stop()
			print("stopping BR")

		if counterBR >= travel_ticks and counterFL >= travel_ticks:
			gameover()
			print("thanks for playing")
			break

#x_axis = [i + 1 for i in range(len(BR_y))]
#BR_y = [val * 1000 for val in range(len( BR_y))]

print("distance to travel is: ", travel_distance)
print(travel_ticks, "ticks are needed to travel ", travel_distance, "m")


print("len(BR_y): ", len(BR_y))
print("len(BR_counter): ", len(BR_counter))
print("len(FL_y): ", len(FL_y))
print("len(FL_counter): ", len(FL_counter))

fig1, ax1 = plt.subplots()
ax1.plot(BR_counter, BR_y, label='BR')
ax1.set_title('back right encoder analysis')
ax1.set_xlabel('GPIO input reading')
ax1.set_ylabel('encoder state')

fig2, ax2 = plt.subplots()
ax2.plot(FL_counter, FL_y, label='FL')
ax2.set_title('front left encoder analysis')
ax2.set_xlabel('GPIO input reading')
ax2.set_ylabel('encoder state')

cv.imshow('initial frame', frame)

plt.show()
gameover()

cv.waitKey(0)
cv.destroyAllWindows()
