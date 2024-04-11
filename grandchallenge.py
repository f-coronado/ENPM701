import RPi.GPIO as GPIO
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import time
from libraries.perception import Perception
from libraries.localization import Localization
from libraries.locomotion import Locomotion

def main():
	perception = Perception()
	localization = Localization()
	locomotion = Locomotion()

	# initialize video parameters
	cap = cv.VideoCapture(0)
	fourcc = cv.VideoWriter_fourcc(*'XVID')
	fps = 10
	out_video = cv.VideoWriter("grand_challenge.avi", fourcc, fps, (640, 480), isColor=True)

	# define color properties
	green_lower = np.array([38, 61, 176])
	green_upper = np.array([237, 188, 255])
	#green_upper = np.array([70, 255, 255])
	#green_upper = np.array([70, 255, 255])

	ret, frame = cap.read()
	if not ret:
		print("failed to capture frame")
		#break

	frame = cv.flip(frame, 0)
	hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
	print("type(hsv_frame): ", type(hsv_frame))
	green_edged = perception.detect_color(hsv_frame, green_lower, green_upper)
	cv.imshow('green_edged', green_edged)
	cv.imshow('frame', frame)
	green_contours, cx, cy = perception.detect_contours(green_edged, frame)
	cv.imshow('green_contours', green_contours)
	cv.waitKey(0)
	cv.destroyAllWindows()


if __name__ == '__main__':
	start = time.time()
	main()
	end = time.time()
	print("time taken: ", abs(end - start), "seconds")
