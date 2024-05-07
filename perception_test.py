from libraries.perception import Perception
import cv2 as cv
import numpy as np
import time

perception = Perception()

def main3():
	while True:
		print("distance in feet is: ", perception.measure_distance())

def main2(frame, color):
	edged = perception.detect_color(frame, color)
	cv.imshow('edged: ', edged)
	#print("result of detect_contours: ", perception.detect_contours(edged, frame), "is of type:" , type(perception.detect_contours(edged, frame)))
	contours, _, _, edged, _, _ = perception.detect_contours(edged, frame)
	cv.imshow("contours", contours)
	cv.waitKey(0)
	cv.destroyAllWindows()
	return None

def main():

	start = time.time()
	perception = Perception()
	file = "output_video.mp4"
	cap = cv.VideoCapture(file)
	fps = cap.get(cv.CAP_PROP_FPS)
	width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
	height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
	fourcc = cv.VideoWriter_fourcc(*'mp4v')
	out = cv.VideoWriter("perception_test.mp4", fourcc, fps, (width, height))
	out_edged = cv.VideoWriter("perception_test_edged.mp4", fourcc, fps, (width, height))
	out_contoured = cv.VideoWriter("perception_test_contour.mp4", fourcc, fps, (width, height))

	while cap.isOpened():
		ret, frame = cap.read()
		if not ret:
			print("could not read frame")
			break
		edged_frame = perception.detect_color(frame, "green")
		out_edged.write(edged_frame)
		frame, cx, cy, edged_contour, w, h = perception.detect_contours(edged_frame, frame)
		out.write(frame)
		out_contoured.write(edged_contour)
	out.release()
	out_edged.release()
	out_contoured.release()
	cap.release()
	end = time.time()
	print("time elapsed: ", end-start)



if __name__ == "__main__":
	#main()
	color = "green"
	frame = cv.imread("sessions/close2_rightofbluewall.jpg")
	main2(frame, color)
	frame = cv.imread("sessions/close2bluewall.jpg")
	main2(frame, color)
	frame = cv.imread("sessions/close2bluewall_620pm.jpg")
	main2(frame, color)
	frame = cv.imread("sessions/far2_rightofbluewall.jpg")
	main2(frame, color)
	frame = cv.imread("sessions/farFromblueWall.jpg")
	main2(frame, color)

	#main3()
