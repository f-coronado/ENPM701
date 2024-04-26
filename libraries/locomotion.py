import RPi.GPIO as GPIO
import time
from .perception import Perception
from .localization import Localization
#import cv2 as cv

class Locomotion:

	def __init__(self):
		self.pwm_pins = [31, 33, 35, 37] # define pins to use
		GPIO.setmode(GPIO.BOARD) # setup GPIO mode
		for pin in self.pwm_pins:
			GPIO.setup(pin, GPIO.OUT) # setup pins as out

		self.pwm_obj = [GPIO.PWM(pin, 50) for pin in self.pwm_pins] # create pwm objects for each pin
		GPIO.setup(12, GPIO.IN, pull_up_down = GPIO.PUD_UP) # setup BR encoder
		GPIO.setup(7, GPIO.IN, pull_up_down = GPIO.PUD_UP) # setup FL encoder

		GPIO.setup(36, GPIO.OUT)
		self.gripper_pwm = GPIO.PWM(36, 50) # setup pin 36 with 50Hz
		self.gripper_pwm.start(3.5) # start gripper in closed position

		self.duty = 80
		self.duty_turn = 60

		#self.cap = cv.VideoCapture(0)
		#self.codec = cv.VideoWriter_fourcc(*'mp4v')

		for pwm_object in self.pwm_obj:
			pwm_object.start(0) # start each pin with duty cycle of 0

		self.perception = Perception()
		self.local = Localization()

	def control_straight(self, direction):

		error =  self.local.counterFL - self.local.counterBR


	def look4color(self, color):

		#out = cv.VideoWriter('look4color.mp4', self.codec, 1, (640, 480))

		if color == "green":
			lower = self.perception.green_lower
			upper = self.perception.green_upper
		elif color == "red":
			lower = self.perception.red_lower
			upper = self.perception.red_upper
		elif color == "blue":
			lower = self.perception.blue_lower
			upper = self.perception.blue_upper

		with self.local.imu_angle_lock:
			self.local.prior_imu_angle = self.local.imu_angle
		print("initial angle: ", self.local.prior_imu_angle)
		time.sleep(3)
		right_turn = 90
		left_turn = 180

		while True:
			frame = self.perception.get_pic()
			#out.write(frame)
			# turn right 90 degrees and look for the color obj
			self.drive([self.duty_turn, 0, self.duty_turn, 0])
			# get edged frame
			edged = self.perception.detect_color(frame, color)
			# if we found the object
			if self.perception.detect_contours(edged, frame) is not None:
				frame, cx, cy, edged, w, h = self.perception.detect_contours(edged, frame)
				#out.write(frame)
				#print("got centroid")
				self.drive([self.duty, 0, 0, self.duty]) # drive straight to obj

			# get current angle
			with self.local.imu_angle_lock:
				self.local.lr_imu_angle = self.local.imu_angle
			print("current angle: ", self.local.lr_imu_angle)
			# else if the bot has turned right > 90 degrees
			if abs(self.local.prior_imu_angle - self.local.lr_imu_angle) >= right_turn:
				print("turned right by 90 degrees")
				frame = self.perception.get_pic()
				#out.write(frame)
				break

		# update prior imu_angle
		with self.local.imu_angle_lock:
			self.local.prior_imu_angle = self.local.imu_angle
		print("updated angle is: ", self.local.prior_imu_angle)

		while True:
			frame = self.perception.get_pic()
			#out.write(frame)
			self.drive([0, self.duty_turn, 0, self.duty_turn]) # turn left
			# check for object
			edged = self.perception.detect_color(frame, color)
			if self.perception.detect_contours(edged, frame) is not None:
				frame, cx, cy, edged, w, h = self.perception.detect_contours(edged, frame)
				#print("got centroid")
				#frame = self.perception.get_pic()
				#out.write(frame)
			# get current angle
			with self.local.imu_angle_lock:
				self.local.lr_imu_angle = self.local.imu_angle
			print("current angle: ", self.local.lr_imu_angle)

			# else if the bot has turned left > 180 degrees
			if abs(self.local.prior_imu_angle - self.local.lr_imu_angle) >= left_turn:
				print("turned left by 180 degrees")
				frame = self.perception.get_pic()
				#out.write(frame)
				break
		#out.release()


	def drive(self, duty_cycle):
	# To drive forward: pins 31 and 37 true, pins 33 and 35 false
	# To drive in reverse: pins 31 and 37 false, pins 33 and 35 true
	# To pivot left: Pins 33 and 37 true, Pins 31 and 35 false
	# To pivot right: Pins 31 and 35 true, Pins 33 and 37 false
	# format is [31, 33, 35, 37]
		for pwm_object, duty in zip(self.pwm_obj, duty_cycle):
			pwm_object.ChangeDutyCycle(duty)

	def grip(self, position):
	# 3.5 = close, 5.5 = half, 7.5 = open
		if position == "open":
			print("opening gripper")
			self.gripper_pwm.ChangeDutyCycle(7.5)
		if position == "half":
			print("half opening gripper")
			self.gripper_pwm.ChangeDutyCycle(5.5)
		if position == "close":
			print("closing gripper")
			self.gripper_pwm.ChangeDutyCycle(3.5)


	def get_object(self, cap, color, frame):

		start = time.time()
		edged_frame = self.perception.detect_color(frame, color)
		frame, cx, cy, edged_frame, w, h = self.perception.detect_contours(edged_frame, frame)
		end = time.time()
		print("time taken to capture edge and contour within get_object", end-start)

		if self.perception.object_check(w, h) is True:
			print("object is within grasp")
			self.drive([0, 0, 0, 0])
			self.grip("open") # open before we drive object into gripper opening
			time.sleep(3)
			start = time.time()

			while True:
				self.drive([40, 0, 0, 40]) # drive to grab object
				_, _ = self.local.get_tick_count() # update tick count
				#print("driving into object to grasp")
				# 3 inches = .0732m, and 4687 ticks/m
				if self.local.counterFL >= .0762 * 4687:
					break
			end = time.time()
			print("time taken through while loop in get_object: ", end-start)
			self.grip("close")
			self.drive([0, 0, 0, 0])
			time.sleep(3)
			return True


	def gameover(self):

		print("stopping ... ")
		GPIO.output(31, False)
		GPIO.output(33, False)
		GPIO.output(35, False)
		GPIO.output(37, False)
		time.sleep(2)

#	        GPIO.cleanup()

