import RPi.GPIO as GPIO
import time
from .perception import Perception
from .localization import Localization
import cv2 as cv

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

		self.duty = 60
		self.duty_turn = 60 # 35 works best on desktop, 70 works best on floor
		self.reduce = 10

		#self.cap = cv.VideoCapture(0)
		#self.codec = cv.VideoWriter_fourcc(*'mp4v')

		for pwm_object in self.pwm_obj:
			pwm_object.start(0) # start each pin with duty cycle of 0

		self.perception = Perception()
		self.local = Localization()

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
		#print("initial angle: ", self.local.prior_imu_angle)
		#time.sleep(3)
		right_turn = 90
		left_turn = 180

		while True:
			frame = self.perception.get_pic()
			# turn right 90 degrees and look for the color obj
			self.drive([self.duty_turn - self.reduce, 0, self.duty_turn - self.reduce, 0])
			# get edged frame
			edged = self.perception.detect_color(frame, color)
			# if we found the object
			#if self.perception.detect_contours(edged, frame) is not None:
			frame, cx, cy, edged, w, h = self.perception.detect_contours(edged, frame)
			#print("contours is not none")
			text = "obj is" + str(self.perception.get_angle2center(cx)) + "degrees from center"
			frame = self.perception.write_on_frame(frame, text)
			cv.imshow("contours: ", frame)
			cv.waitKey(30)
			# and the obj is close to the center
			#print("angle2center: ", self.perception.get_angle2center(cx))
			if abs(self.perception.get_angle2center(cx)) <= 2:
				self.drive([0, 0, 0, 0]) # stop
				print("cx: ", cx, "cy: ", cy)
				#cv.imshow("centerd obj", frame)
				time.sleep(10)
				print("waiting before get_object")
				self.get_object(color, frame)
				time.sleep(10000)

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
			frame = self.perception.get_pic() # look for obj
			self.drive([0, self.duty_turn - self.reduce, 0, self.duty_turn - self.reduce]) # turn left
			# check for object
			edged = self.perception.detect_color(frame, color)
			if self.perception.detect_contours(edged, frame) is not None:
				frame, cx, cy, edged, w, h = self.perception.detect_contours(edged, frame)
				print("contours is not none")
				cv.imshow("contours: ", frame)
				cv.waitKey(30)
				# and the obj is close to the center
				print("angle2center: ", self.perception.get_angle2center(cx))
				if abs(self.perception.get_angle2center(cx)) <= 2:
					self.drive([0, 0, 0, 0]) # stop
					print("cx: ", cx, "cy: ", cy)
					cv.imshow("centerd obj", frame)
					print("waiting before get_object")
					self.get_object(color, frame)
					time.sleep(10000)

			# get current angle
			with self.local.imu_angle_lock:
				self.local.lr_imu_angle = self.local.imu_angle
			print("current angle: ", self.local.lr_imu_angle)

			# if the bot has turned left > 180 degrees
			if abs(self.local.prior_imu_angle - self.local.lr_imu_angle) >= left_turn:
				print("turned left by 180 degrees")
				frame = self.perception.get_pic()
				#out.write(frame)
				break


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


	def get_object(self, color, frame):
		print("\ngetting obj")
		start = time.time()
		edged_frame = self.perception.detect_color(frame, color)
		frame, cx, cy, edged_frame, w, h = self.perception.detect_contours(edged_frame, frame)
		end = time.time()
		print("time taken to capture edge and contour within get_object", end-start)

		while True:
			frame = self.perception.get_pic()
			self.drive([self.duty, 0, 0, self.duty]) # drive straight to obj
			edged_frame = self.perception.detect_color(frame, color)
			frame, cx, cy, edged_frame, w, h = self.perception.detect_contours(edged_frame, frame)
			print("cx: ", cx, "angle2center: ", self.perception.get_angle2center(cx))
			if self.perception.get_angle2center(cx) >= 7: # if obj to right more than 7 degrees
				print("obj is to right ", cx, "degrees")
				# turn right 
				self.drive([self.duty_turn - 10, 0, self.duty_turn - 10, 0])
				while True:
					frame = self.perception.get_pic()
					edged = self.perception.detect_color(color)
					frame, cx, cy, edged, w, h = perception.detect_contours(edged, frame)
					if cx <= 7:
						break
			elif self.perception.get_angle2center(cx) <= -7: # if obj to left more than 7 degrees
				print("obj is to left ", cx, "degrees")
				# turn left
				self.drive([0, self.duty_turn - 10, 0,  self.duty_turn - 10])
				while True:
					frame = self.perception.get_pic()
					edged = self.perception.detect_color(color)
					frame, cx, cy, edged, w, h = perception.detect_contours(edged, frame)
					if self.perception.get_angle2center(cx) >= -7:
						break
			cv.imshow("frame: ", frame)
			cv.waitKey(30)
			if self.perception.object_check(w, h) is "open": # obj is near
				print("object is near, opening gripper")
				self.drive([0, 0, 0, 0]) # stop
				self.grip("open") # open gripper
				break

		print("obj should be close and centered enough by now")
		# obj should be close and center enough by now
		self.drive([self.duty, 0, 0, self.duty])
		while True:
			frame = self.perception.get_pic()
			edged = self.perception.detect_color(frame, color)
			frame, cx, cy, _, w, h = self.perception.detect_contours(edged, frame)
			cv.imshow("frame", frame)
			cv.waitKey(30)
			print("w: ", w, "h: ", h)
			# if w > 100 and h > 145
			#object is close enough so...
			if self.perception.object_check(w, h) is "grip":
				#print("object is within grasp")
				#self.drive([0, 0, 0, 0]) # stop
				#self.grip("open") # open before we drive object into gripper opening
				#time.sleep(2)
				#start = time.time()

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

