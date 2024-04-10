import RPi.GPIO as gpio
import cv2 as cv
import numpy as np
import time

def add_channels(frame):
        frame = np.expand_dims(frame, axis = -1)
        frame = np.repeat(frame, 3, axis = -1)

        return frame


def get_center_distance(cx):
	angle = (cx - 320) * .061
	return angle

def detect_color(hsv_frame, lower_hsv, upper_hsv):
	mask_video = cv.inRange(hsv_frame, lower_hsv, upper_hsv)
	cv.imshow('masked frame', mask_video)
	blurred_video = cv.GaussianBlur(mask_video, (5,5), 0)
	blurred_video = add_channels(blurred_video)
	gray_video = cv.cvtColor(blurred_video, cv.COLOR_BGR2GRAY)
	edged_video = cv.Canny(gray_video, 40, 220)
	cv.imshow('edged frame', edged_video)
	cv.destroyAllWindows()

	return edged_video

def detect_contours(edged_video):

	contours_, hierarchy_ = cv.findContours(edged_video, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
	cv.drawContours(edged_video, contours_, -1, (255, 0, 0), 2)

	for contour_ in contours_:
		M = cv.moments(contour_)
#		print('M: ', M)
		if M['m00'] != 0:
			cx = int(M['m10'] / M['m00'])
			cy = int(M['m01'] / M['m00'])
			cv.circle(edged_video, (cx, cy), 1, (0, 255, 255), 1)

		(x, y), radius = cv.minEnclosingCircle(contour_)
		center = (int(x), int(y))
		radius = int(radius)

		cv.circle(edged_video, center, radius, (0, 0, 255), 2)

	return edged_video, cx, cy


def main():
	cap = cv.VideoCapture(0)
	fourcc = cv.VideoWriter_fourcc(*'XVID')
	out = cv.VideoWriter('turn2angle.mp4', fourcc, 10, (640, 480))

	lower_green = np.array([30, 40, 40])
	upper_green = np.array([70, 255, 255])

	begin = time.time()

#	while(cap.isOpened()):
	while time.time() - begin < 1:
		ret, frame = cap.read()

		if not ret:
			print("could not capture frame")
			break
		frame = cv.flip(frame, 0)
		green_frame = detect_color(frame, lower_green, upper_green)
		green_frame, cx, cy = detect_contours(green_frame)
		angle_from_center = get_center_distance(cx)
		cv.imwrite('original_frame.jpg', frame)
		cv.imwrite('green_frame.jpg', green_frame)
		#cv.imshow('green_frame', green_frame)

	cap.release()
	out.release()
	#cv.waitKey(0)
	cv.destroyAllWindows()

if __name__ == '__main__':

	start = time.time()
	main()
	end = time.time()
	print("time taken: ", abs(start-end))
