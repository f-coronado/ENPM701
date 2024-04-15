import serial
import RPi.GPIO as GPIO
from libraries.localization import Localization
from libraries.locomotion import Locomotion
from libraries.perception import Perception
import matplotlib.pyplot as plt
import time
import cv2 as cv


def main():

	locomotion = Locomotion()
	localization = Localization()
	perception = Perception()
	print("successfully loaded libraries")

	cap = cv.VideoCapture(0) # assign camera
	codec = cv.VideoWriter_fourcc(*'XVID')
	out = cv.VideoWriter('trackblock.avi',codec, 5, (640,480))

	width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
	height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
	font = cv.FONT_HERSHEY_SIMPLEX
	white = (255, 255, 255)

	while(cap.isOpened()):
#		print("cap is opened")
		ret, frame = cap.read()
		frame = cv.flip(frame, -1) # flip frame vertically and horizontally
		# draw horizontal crosshair
		cv.line(frame, (0, int(frame.shape[0]/2)), (int(frame.shape[1]), int(frame.shape[0]/2)), (0, 0, 0), 1)
		# draw vertical crosshair
		cv.line(frame, (int(frame.shape[1]/2), 0), (int(frame.shape[1]/2), int(frame.shape[0])), (0, 0, 0), 1)
#		print("center of frame is at (", int(frame.shape[1]/2), ",", int(frame.shape[0]/2), ")")
		if not ret:
			print("unable to read frame")
		hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
		green_lower = (38, 61, 176)
		green_upper = (237, 188, 255)
		green_frame = perception.detect_color(hsv_frame, green_lower, green_upper)
		frame, cx, cy = perception.detect_contours(green_frame, frame)
#		print("cx: ", cx, "cy: ", cy)
#		cv.imshow('centroids: ', frame)
		perception.get_angle2center(cx)
#		print('block is ', perception.angle_2_center, 'degrees from the center')

		dutyturn = 60

		if perception.angle_2_center >= 0:
			locomotion.drive([dutyturn, 0, dutyturn, 0])
			print("turning right")
			cv.putText(frame, 'turning right', (100, 400), font, 1, white, 2)
		if perception.angle_2_center <= 0:
			locomotion.drive([0, dutyturn, 0, dutyturn])
			cv.putText(frame, 'turning left', (100, 400), font, 1, white, 2)
			print("turning left")

		out.write(frame)

	#	if cv.waitKey(100001) & 0xFF == ord('q'): 
	#		break
	print("broke out of while loop")

#	cv.destroyAllWindows()
	cap.release()

if __name__ == "__main__":
	main()
