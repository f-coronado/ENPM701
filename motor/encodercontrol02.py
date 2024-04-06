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

counter = np.uint64(0)
button = int(0)

# initialize pwm signal to control motor
#gpio.setup(36, gpio.OUT)
#pwm = gpio.PWM(36, 50)
#pwm.start(7.5)

time.sleep(0.1)
right_wheels()

x_vals = []
y_vals = []

with open('encodercontrol02.txt', 'w') as file: # open this file in write mode
	file.write("Counter\t GPIO state\n") 

	for i in range(0, 100000):
		file.write(f"{counter}\t{gpio.input(12)}\n") # write to the file

		x_vals.append(gpio.input(12))
		y_vals.append(counter)

		print("counter = ", counter, "GPIO state: ", gpio.input(12))

		if int(gpio.input(12)) != int(button):
			button = int(gpio.input(12))
			counter += 1

		if counter >= 960:
#			pwm.stop()
			gameover()
			print("thanks for playing")
			break

x_vals = [x * 1000 for x in x_vals]
gpio_list = [i + 1 for i in range(len(x_vals))]

#print("x_vals: ", x_vals)
#print("idx: ", idx)
print("len(x_vals): ", len(x_vals))

plt.plot(gpio_list, x_vals)
plt.xlabel('GPIO input reading')
plt.ylabel('Encoder State')
plt.title('Motor Encoder Analysis')
plt.show()
gameover()
