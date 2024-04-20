import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import time
import os

class Perception:

	def __init__(self):
		self.angle_2_center = 10000
		self.white = (255, 255, 255)
		self.black = (0, 0, 0)
		self.font = cv.FONT_HERSHEY_SIMPLEX

	def add_channels(self, frame):
		frame = np.expand_dims(frame, axis = -1)
		frame = np.repeat(frame, 3, axis = -1)
		return frame

	def get_angle2center(self, cx):
		self.angle_2_center = int((cx - 320) * .061)
		return self.angle_2_center

	def detect_color(self, frame, lower_hsv, upper_hsv):
		hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
		mask_video = cv.inRange(hsv_frame, lower_hsv, upper_hsv)
		#cv.imshow('masked frame', mask_video)
		blurred_video = cv.GaussianBlur(mask_video, (5,5), 0)
		blurred_video = self.add_channels(blurred_video)
		gray_video = cv.cvtColor(blurred_video, cv.COLOR_BGR2GRAY)
		edged_video = cv.Canny(gray_video, 40, 220)
		#cv.imshow('edged frame', edged_video)
		#cv.destroyAllWindows()

		return edged_video

	def detect_contours(self, edged_frame, bgr_frame):

		contours_, hierarchy_ = cv.findContours(edged_frame, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
		cv.drawContours(edged_frame, contours_, -1, (255, 0, 0), 2) # not sure if i need this

		for contour_ in contours_:
			M = cv.moments(contour_)
			#               print('M: ', M)
			if M['m00'] != 0:
				cx = int(M['m10'] / M['m00'])
				cy = int(M['m01'] / M['m00'])
				cv.circle(bgr_frame, (cx, cy), 1, (0, 255, 255), 1)

			(x, y), radius = cv.minEnclosingCircle(contour_)
			center = (int(x), int(y))
			radius = int(radius)

			cv.circle(bgr_frame, center, radius, (0, 0, 255), 2)
			cv.putText(bgr_frame, 'circle radius is' + str(radius), (100, 100), self.font, 1, self.white, 1)

		return bgr_frame, cx, cy

	def detect_qr_code(self):

		command = 'sudo modprobe bcm2835-v4l2'
		os.system(command)

		# open video capture
		cap = cv.VideoCapture(0)

		# define detector
		detector = cv.QRCodeDetector()

		while True:
			check, img = cap.read()
			data, bbox, _ = detector.detectAndDecode(img)

			if(bbox is not None):
				for i in range(len(bbox)):
					cv.line(img, tuple(bbox[i][0]), tuple(bbox[(i+1) % len(bbox)][0]), color=(0, 0, 255), thickness = 4)
					cv.putText(img, data, (int(bbox[0][0][0]), int(bbox[0][0][1]) - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0) ,2)
			if data:
				print("Data: ", data)
			# show results to the screen
			cv.imshow("QR code detector", img)

			# break out of the loop by pressing the q key
			if(cv.waitKey(1) == ord("q")):
				break

		cap.release()
		cv.destroyAllWindows()


#	def trackblock(
