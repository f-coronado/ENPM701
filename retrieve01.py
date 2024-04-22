import cv2 as cv
from libraries.locomotion import Locomotion
from libraries.perception import Perception
import time

def main():

	start = time.time()
	perception = Perception()
	locomotion = Locomotion()
	file = "output_video.mp4"
	cap = cv.VideoCapture(file)
	fps = cap.get(cv.CAP_PROP_FPS)
	width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
	height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
	fourcc = cv.VideoWriter_fourcc(*'mp4v')
	out = cv.VideoWriter("retrieve01.mp4", fourcc, fps, (width, height))

	while cap.isOpened():
		ret, frame = cap.read()
		if not ret:
			print("could not read frame")
			break
		locomotion.get_object(cap, "green", frame)
		out.write(frame)
	out.release()
	cap.release()
	end = time.time()
	print("time elapsed: ", end-start)

if __name__ == "__main__":
	main()
