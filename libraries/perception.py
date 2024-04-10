import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import time

class Perception:

	def add_channels(self, frame):
		frame = np.expand_dims(frame, axis = -1)
		frame = np.repeat(frame, 3, axis = -1)
		return frame

	def get_center_distance(self, cx):
		angle = (cx - 320) * .061
		return angle

	def detect_color(self, hsv_frame, lower_hsv, upper_hsv):
		mask_video = cv.inRange(hsv_frame, lower_hsv, upper_hsv)
		cv.imshow('masked frame', mask_video)
		blurred_video = cv.GaussianBlur(mask_video, (5,5), 0)
		blurred_video = self.add_channels(blurred_video)
		gray_video = cv.cvtColor(blurred_video, cv.COLOR_BGR2GRAY)
		edged_video = cv.Canny(gray_video, 40, 220)
		cv.imshow('edged frame', edged_video)
		cv.destroyAllWindows()

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

		return bgr_frame, cx, cy
