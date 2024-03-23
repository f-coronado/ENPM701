import RPi.GPIO as gpio
import time

# define pin allocations
trig = 16
echo = 18

def distance():
	gpio.setmode(gpio.BOARD)
	gpio.setup(trig, gpio.OUT)
	gpio.setup(echo, gpio.IN)
	
	# ensure output has no value
	gpio.output(trig, False)
	time.sleep(0.01)
	
	# generate trigger pulse
	gpio.output(trig, True)
	time.sleep(0.00001)
	gpio.output(trig, False)

	# generate echo time signal
	while gpio.input(echo) == 0:
		pulse_start = time.time()
	
	while gpio.input(echo) == 1:
		pulse_end = time.time()

	pulse_duration = pulse_end - pulse_start

	# convert time to distance
	distance = pulse_duration * 17150
	distance = round(distance, 2)

	# cleanup gpio pins and return distance estimate
	gpio.cleanup()
	return distance

print("Distance: ", distance(), "cm")

