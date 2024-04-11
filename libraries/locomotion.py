import RPi.GPIO as GPIO

class Locomotion:

	def __init__(self):
		self.pwm_pins = [31, 33, 35, 37] # define pins to use
		GPIO.setmode(GPIO.BOARD) # setup GPIO mode
		for pin in self.pwm_pins:
			GPIO.setup(pin, GPIO.OUT) # setup pins as out

		self.pwm_obj = [GPIO.PWM(pin, 50) for pin in self.pwm_pins] # create pwm objects for each pin
		GPIO.setup(12, GPIO.IN, pull_up_down = GPIO.PUD_UP) # setup BR encoder
		GPIO.setup(7, GPIO.IN, pull_up_down = GPIO.PUD_UP) # setup FL encoder

		for pwm_object in self.pwm_obj:
			pwm_object.start(0) # start each pin with duty cycle of 0

	def drive(self, duty_cycle):
		for pwm_object, duty in zip(self.pwm_obj, duty_cycle):
			pwm_object.ChangeDutyCycle(duty)


	def gameover(self):

	        GPIO.output(31, False)
	        GPIO.output(33, False)
	        GPIO.output(35, False)
	        GPIO.output(37, False)

#	        GPIO.cleanup()

