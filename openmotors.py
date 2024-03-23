import RPi.GPIO as gpio

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

	gpio.cleanup()

init()
gameover()


