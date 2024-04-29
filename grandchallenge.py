import RPi.GPIO as GPIO
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import time
from libraries.perception import Perception
from libraries.localization import Localization
from libraries.locomotion import Locomotion

def main():

	### intialization ###

	# classes
	perc = Perception()
	local = Localization()
	loco = Locomotion()

	# video parameters
	cap = cv.VideoCapture(0)
	fourcc = cv.VideoWriter_fourcc(*'mp4v')
	fps = 10
	out_video = cv.VideoWriter("grand_challenge.mp4", fourcc, fps, (640, 480), isColor=True)

	### loop1: look for QR code ###


	### loop2: start ###


	### loop3: retrieve and deliver ###










	order = ['r', 'g', 'b', 'r', 'g', 'b', 'r', 'g', 'b']
	for color in order:

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
