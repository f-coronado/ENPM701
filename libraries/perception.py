import RPi.GPIO as GPIO
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import time
import os
import multiprocessing

class Perception:

	def __init__(self):
		self.angle_2_center = 10000
		self.white = (255, 255, 255)
		self.black = (0, 0, 0)
		self.font = cv.FONT_HERSHEY_SIMPLEX
		self.green_lower = (38, 45, 95) # values for home 4/21
		self.green_upper = (65, 220, 255) # values for home 4/21
		self.blue_lower = (72, 46, 64) # values from session1
		self.blue_upper = (152, 178, 220) # values from session1
		self.red_lower = (167, 69, 141) # values from session1
		self.red_upper = (183, 170, 255) # values from session1
		self.cap = cv.VideoCapture(0)
		self.codec = cv.VideoWriter_fourcc(*'mp4v')
		GPIO.setmode(GPIO.BOARD)
		self.trig = 16
		self.echo = 18
		GPIO.setup(self.trig, GPIO.OUT)
		GPIO.setup(self.echo, GPIO.IN)

		#self.dist2wall = multiprocessing.Value('f', 0)
		#self.distance_process = multiprocessing.Process(target=self.measure_distance)
		#self.distance_process.daemon=True
		#self.distance_process.start()
		#print("distance process started")
		self.dist2wall = 0

	def measure_distance(self):
		GPIO.output(self.trig, False)
		i = 0

#		while True:
		time.sleep(0.01)

		# generate self.trigger pulse
		GPIO.output(self.trig, True)
		time.sleep(0.00001)
		GPIO.output(self.trig, False)

		# generate self.echo time signal
		while GPIO.input(self.echo) == 0:
			#print("echo = 0", i)
			pulse_start = time.time()
			#echo_cnt += 1
			#if echo_cnt >= 100:
			#	break

		while GPIO.input(self.echo) == 1:
			#print("echo = 1", i)
			pulse_end = time.time()
			#echo_cnt += 1
			#if echo_cnt >= 100:
				#break

		pulse_duration = pulse_end - pulse_start

		# convert time to distance [feet]
		self.dist2wall = round(((pulse_duration * 17150) / 2.54)*(1/12), 2)
		return self.dist2wall


	def get_pic(self):
		ret, frame = self.cap.read()
		if not ret:
			print("couldn't capture frame")
		frame = cv.flip(frame, -1)
		return frame

	def write_on_frame(self, frame, text):
		cv.putText(frame, text, (100, 20), self.font, 1, self.white, 2)
		return frame

	def add_channels(self, frame):
		frame = np.expand_dims(frame, axis = -1)
		frame = np.repeat(frame, 3, axis = -1)
		return frame

	def get_angle2center(self, cx):
		self.angle_2_center = int((cx - 320) * .061)
		return self.angle_2_center

	def detect_color(self, frame, color):
		if color == "red":
			lower_hsv = self.red_lower
			upper_hsv = self.red_upper
		elif color == "green":
			lower_hsv = self.green_lower
			upper_hsv = self.green_upper
		elif color == "blue":
			lower_hsv = self.blue_lower
			upper_hsv = self.blue_upper

		hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
		mask_video = cv.inRange(hsv_frame, lower_hsv, upper_hsv)
		blurred_video = cv.GaussianBlur(mask_video, (3,3), 0)
		blurred_video = self.add_channels(blurred_video)
		gray_video = cv.cvtColor(blurred_video, cv.COLOR_BGR2GRAY)
		edged_video = cv.Canny(gray_video, 40, 220)

		return edged_video

	def detect_contours(self, edged_frame, bgr_frame):

		contours_, hierarchy_ = cv.findContours(edged_frame, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
		if not contours_:
			cx = 800
			cy = 800
			w = 0
			h = 0
			# we always want to return something
			return bgr_frame, cx, cy, edged_frame, w, h
		areas = [cv.contourArea(c) for c in contours_]
		max_idx = np.argmax(areas)
		cont = contours_[max_idx]
		x, y, w, h = cv.boundingRect(cont)
		cv.rectangle(bgr_frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
		#text = f"width: {w}. height: {h}"
		#cv.putText(bgr_frame, text, (x - 100, y), self.font, 1, self.white, 2)
		cx = int(x + w/2)
		cy = int(y + h/2)

		return bgr_frame, cx, cy, edged_frame, w, h

	def object_check(self, w, h):
		#if w >= 160 and h >= 65:
		#	return True
		#elif w >= 120 and h >= 140:
		#	return True
		if w > 210:
			return "grip"

		elif w >= 70 and h >= 100:
			return "open"
		else:
			return False


	def detect_qr_code(self):

		command = 'sudo modprobe bcm2835-v4l2'
		os.system(command)
		# define detector
		detector = cv.QRCodeDetector()

		while True:
			img = self.get_pic()

			data, bbox, _ = detector.detectAndDecode(img)

			if(bbox is not None):
				for i in range(len(bbox)):
					cv.line(img, tuple(bbox[i][0]), tuple(bbox[(i+1) % len(bbox)][0]), color=(0, 0, 255), thickness = 4)
					cv.putText(img, data, (int(bbox[0][0][0]), int(bbox[0][0][1]) - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0) ,2)

			# show results to the screen
			cv.imshow("QR code detector", img)
			# break out of the loop by pressing the q key
			cv.waitKey(30)
			#if(cv.waitKey(1) == ord("q")):
			if data:
				print("Data: ", data)
				break
		cv.destroyAllWindows()
		return data
