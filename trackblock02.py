import serial
import RPi.GPIO as GPIO
from libraries.localization import Localization
from libraries.locomotion import Locomotion
from libraries.perception import Perception
import matplotlib.pyplot as plt
import time
import cv2 as cv


def get_imu_angle(ser, cnt):
	
	if (ser.in_waiting > 0):
		line = ser.readline()
		print(line)
	if cnt > 10:

	line = ser.readline()
	line = line.rstrip().lstrip()
	line = str(line)
	line = line.strip("'")
	line.strip("b'")
	values = line.split()
	values = values[1:]
	values[0] = values[0][:-5]
	values[1] = values[1][:-5]
	x = float(values[0])
	y = float(values[1])
	z = float(values[2])
	if (x >= 180):
		angle = x - 360
	else:
		angle = x

	return angle


def main():

	locomotion = Locomotion()
	localization = Localization()
	perception = Perception()
	print("successfully loaded libraries")

	cap = cv.VideoCapture(0) # assign camera
	codec = cv.VideoWriter_fourcc(*'MJPG')
	out = cv.VideoWriter('trackblock.mp4',codec, 1, (640,480))

	width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
	height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
	font = cv.FONT_HERSHEY_SIMPLEX
	white = (255, 255, 255)
	ser = serial.Serial('/dev/ttyUSB0', 9600)
	cnt = 0
	green_lower = (38, 61, 176)
	green_upper = (237, 188, 255)



	while(cap.isOpened()):
		ret, frame = cap.read()
		if not ret:
			print("unable to read frame")
		frame = cv.flip(frame, -1) # flip frame vertically and horizontally
		# draw horizontal crosshair
		cv.line(frame, (0, int(frame.shape[0]/2)), (int(frame.shape[1]), int(frame.shape[0]/2)), (0, 0, 0), 1)
		# draw vertical crosshair
		cv.line(frame, (int(frame.shape[1]/2), 0), (int(frame.shape[1]/2), int(frame.shape[0])), (0, 0, 0), 1)
		# drawing left bound
		cv.line(frame, (280, 0), (280, 480), (255, 255, 255), 1)
		# drawing right bound
		cv.line(frame, (360, 0), (360, 480), (255, 255, 255), 1)

		# detect green objects
		green_frame = perception.detect_color(frame, green_lower, green_upper)
		# draw contour and get pixel centroid
		frame, cx, cy = perception.detect_contours(green_frame, frame)
		# convert pixel location to angle
		cx = perception.get_angle2center(cx)

		# get the angle, assign it as prior angle b4 we start turning
		localization.prior_imu_angle = get_imu_angle(ser, cnt)
		if localization.prior_imu_angle >= 180:
			localization.prior_imu_angle -= 360
		print("prior angle:")
		print("before turning, robot angle is at: ", localization.prior_imu_angle)

		# get the angle to turn by and assign it as d_angle
		localization.d_angle = perception.get_angle2center(cx)
		print('object is at', cx, 'degrees')

		dutyturn = 60
		# if object is 5 degrees or more to the right
		if cx >= 5:
			print('\nneed to turn right by', cx, "degrees")
			print("current angle: ", get_imu_angle(ser, cnt))
			print("abs(current angle - prior angle) = ",abs(get_imu_angle(ser, cnt) - localization.prior_imu_angle))

			# while the difference in prior and current angle <= turn angle
			while abs(get_imu_angle(ser, cnt) - localization.prior_imu_angle) <= cx:
				print("		abs(current angle - prior angle) = ",get_imu_angle(ser, cnt) - localization.prior_imu_angle)
				locomotion.drive([dutyturn, 0, dutyturn, 0]) # pivot right
#				print("		current angle is:", get_imu_angle(ser, cnt), "degrees")
				print("		turned right by", get_imu_angle(ser, cnt) - localization.prior_imu_angle, "degrees")
				ret, frame = cap.read()
				frame = cv.flip(frame, -1)
				green_frame = perception.detect_color(frame, green_lower, green_upper)
				frame, cx, cy = perception.detect_contours(green_frame, frame)
				cx = perception.get_angle2center(cx)
				cv.putText(frame, 'turning right, block is' + str(perception.angle_2_center) + 'degrees from the center', (100, 400), font, 1, white, 2)
				out.write(frame)
			locomotion.gameover() # stop turning
			print("turned to object")

		elif cx <= -5:
			print("need to turn left by", abs(cx), "degrees")
			print("current angle: ", get_imu_angle(ser, cnt))
			print("abs(current angle - prior angle) = ",abs(get_imu_angle(ser, cnt) - localization.prior_imu_angle))

			# while the difference in prior and current angle <= turn angle
			while abs(get_imu_angle(ser, cnt) - localization.prior_imu_angle) <= abs(cx):
				locomotion.drive([0, dutyturn, 0, dutyturn]) # pivot left
#				print("		current angle is:", localization.imu_angle, "degrees")
				print("		abs(current angle - prior angle) = ",abs(get_imu_angle(ser, cnt) - localization.prior_imu_angle))
				print("		turned left by", get_imu_angle(ser, cnt) - localization.prior_imu_angle, "degrees")
				ret, frame = cap.read()
				frame = cv.flip(frame, -1)
				green_frame = perception.detect_color(frame, green_lower, green_upper)
				frame, cx, cy = perception.detect_contours(green_frame, frame)
				cx = perception.get_angle2center(cx)
				cv.putText(frame, 'turning left, block is' + str(perception.angle_2_center) + 'degrees from the center', (100, 400), font, 1, white, 2)
				out.write(frame)
			locomotion.gameover() # stop turning
			print("turned to object")

		out.write(frame)
	cap.release()
	out.release()

if __name__ == "__main__":
	main()
