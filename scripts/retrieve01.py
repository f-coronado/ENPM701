import cv2 as cv
from libraries.locomotion import Locomotion
from libraries.perception import Perception
from libraries.localization import Localization
import time

def main():

	start = time.time()
	perception = Perception()
	locomotion = Locomotion()
	local = Localization()
	#file = "output_video.mp4"
	#cap = cv.VideoCapture(file)
	#fps = cap.get(cv.CAP_PROP_FPS)
	fps = 1
	#width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
	#height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
	cap = cv.VideoCapture(0)
	width = 640
	height = 480
	fourcc = cv.VideoWriter_fourcc(*'mp4v')
	out = cv.VideoWriter("retrieve01.mp4", fourcc, fps, (width, height))
	duty = 60

	while cap.isOpened():
		ret, frame = cap.read()
		frame = cv.flip(frame, -1)
		#cv.imshow("live feed", frame)
		if not ret:
			print("could not read frame")
			break
		print("inside get_object function")
		status = locomotion.get_object(cap, "green", frame)
		out.write(frame)
		start = time.time()
		if status == True:
			print("got obj")
			out.write(frame)
			break

		else:
			local.get_tick_count()
			print("FL cnt: ", local.counterFL, "BR cnt: ", local.counterBR)
			out.write(frame)
			#print("driving to obj")
			locomotion.drive([duty, 0, 0, duty])
		end = time.time()
		print("time taken for else statement in retrieve01.py", end-start)

	cv.destroyAllWindows()
	out.release()
	cap.release()
	end = time.time()
	print("time elapsed: ", end-start)

if __name__ == "__main__":
	main()
