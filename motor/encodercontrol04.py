import RPi.GPIO as gpio
import time
import numpy as np
import matplotlib.pyplot as plt

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

def right_wheels():

	init()

	gpio.output(35, False)
	gpio.output(37, True)
	time.sleep(2)

	#gameover()

## main code ##
init()
counterFL = np.uint64(0)
counterBR = np.uint64(0)

buttonFL = int(0)
buttonBR = int(0)

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
		print("counterBR: ", counterBR, "counterFL: ", counterFL, "BR state: ", gpio.input(12), "FL state: ", gpio.input(7))
		file.write(f"{counterBR}\t{gpio.input(12)}\t{counterFL}\t{gpio.input(7)}\n") # write to the file

		BR_y.append(gpio.input(12))
		FL_y.append(gpio.input(7))

		if int(gpio.input(12)) != int(buttonBR):
			buttonBR = int(gpio.input(12))
			counterBR += 1
			BR_counter.append(counterBR)

		if int(gpio.input(7)) != int(buttonFL):
			buttonFL = int(gpio.input(7))
			counterFL += 1
			FL_counter.append(counterFL)

		if counterFL >= 960:
			pwmBL.stop()

		if counterBR >= 960:
			pwmFR.stop()

		if counterBR >= 960 and counterFL >= 960:
			gameover()
			print("thanks for playing")
			break


print("len(BR_y): ", len(BR_y))
print("len(BR_counter): ", len(BR_counter))
print("len(FL_y): ", len(FL_y))
print("len(FL_counter): ", len(FL_counter))


#plt.plot(x_vals, y_vals)
#plt.xlabel('GPIO input reading')
#plt.ylabel('Encoder State')
#plt.title('Motor Encoder Analysis')
#plt.show()
gameover()
