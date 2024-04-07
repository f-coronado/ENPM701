import RPi.GPIO as GPIO
import time
import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv

## initialize GPIO pins ##

def init():

	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(31, GPIO.OUT) # IN1
	GPIO.setup(33, GPIO.OUT) # IN2
	GPIO.setup(35, GPIO.OUT) # IN3
	GPIO.setup(37, GPIO.OUT) # IN4

	GPIO.setup(12, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	GPIO.setup(7, GPIO.IN, pull_up_down = GPIO.PUD_UP)

def gameover():

	GPIO.output(31, False)
	GPIO.output(33, False)
	GPIO.output(35, False)
	GPIO.output(37, False)

	GPIO.cleanup()

def get_input():

	distance = float(input("enter how long you want the robot to drive in meters(<1m):"))

	return round(distance, 4)

def get_tick_cnt(dist):

	ticks = (dist * 120 * 8)/.2048

	return ticks 

def add_channels(frame):

	frame = np.expand_dims(frame, axis = -1)
	frame = np.repeat(frame, 3, axis = -1)

	return frame

def detect_green(hsv_frame):

	mask_video = cv.inRange(hsv_frame, lower_green, upper_green)
	blurred_video = cv.GaussianBlur(mask_video, (5,5), 0)
	blurred_video = add_channels(blurred_video)
	gray_video = cv.cvtColor(blurred_video, cv.COLOR_BGR2GRAY)
	edged_video = cv.Canny(gray_video, 40, 220)
	contours_, hierarchy_ = cv.findContours(edged_video, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
	cv.drawContours(edged_video, contours, -1, (255, 0, 0), 2)

	for contour_ in contours_:
		M = cv.moments(contour)
		if M['m00'] != 0:
			cx = int(M['m10'] / M['m00'])
			cy = int(M['m01'] / M['m00'])
		(x, y), radius = cv.minEnclosingCircle(contour_)
		center = (int(x), int(y))
		radius = int(radius)

		cv.circle(img, center, radius, (0, 0, 255), 2)
		cv.circle(image, (cx, cy), 1, (0, 255, 255), 1)

	return img


## main code ##
init()
counterFL = np.uint64(0)
counterBR = np.uint64(0)

buttonFL = int(0)
buttonBR = int(0)

# hw7
travel_distance = get_input()
print("distance to travel is: ", travel_distance)
travel_ticks = get_tick_cnt(travel_distance)
print(travel_ticks, "ticks are needed to travel ", travel_distance, "m")

# camera properties intialization
lower_green = (29, 45, 63)
upper_green = (72, 214, 237)
cap = cv.VideoCapture(0)
fourcc = cv.VideoWriter_fourcc(*'XVID')
today = time.strftime("%Y%m%d-%H%M%S")
fps_out = 10
out = cv.VideoWriter("encodercontrol05.avi", fourcc, fps_out, (640, 480), isColor=True)

start_time = cv.getTickCount() / cv.getTickFrequency()


# independent motor control via pwm
pwmBL = GPIO.PWM(31, 50)
pwmFR = GPIO.PWM(37, 50)
val = 22
pwmBL.start(val)
pwmFR.start(val)
time.sleep(0.1)

BR_y = []
FL_y = []
BR_counter = []
FL_counter = []


start_time = cv.getTickCount() / cv.getTickFrequency()
with open('encodercontrol04.txt', 'w') as file: # open this file in write mode
	file.write("BRcnt  BR GPIO  FLcnt  FLGPIO\n") 

	for i in range(0, 100000):
#		ret, frame = cap.read()
#		if not ret:
#			print("failed to capture frame")
#			break
#		frame = cv.flip(frame, 0) # flip vertically
#		cv.imshow('frame', frame)


		print("i: ", i)
		print("counterBR: ", counterBR, "counterFL: ", counterFL, "BR state: ", GPIO.input(12), "FL state: ", GPIO.input(7))
		file.write(f"{counterBR}\t{GPIO.input(12)}\t{counterFL}\t{GPIO.input(7)}\n") # write to the file

		if int(GPIO.input(12)) != int(buttonBR):
			buttonBR = int(GPIO.input(12))
			BR_y.append(GPIO.input(12))
			counterBR += 1
			BR_counter.append(counterBR)

		if int(GPIO.input(7)) != int(buttonFL):
			buttonFL = int(GPIO.input(7))
			FL_y.append(GPIO.input(7))
			counterFL += 1
			FL_counter.append(counterFL)

		if counterFL >= travel_ticks:
			pwmBL.stop()
			print("stopping FL")

		if counterBR >= travel_ticks:
			pwmFR.stop()
			print("stopping BR")

		if counterBR >= travel_ticks and counterFL >= travel_ticks:
			#gameover()
			print("thanks for playing")
			break

#		out.write(frame)

print("distance to travel is: ", travel_distance)
print(travel_ticks, "ticks are needed to travel ", travel_distance, "m")


print("len(BR_y): ", len(BR_y))
print("len(BR_counter): ", len(BR_counter))
print("len(FL_y): ", len(FL_y))
print("len(FL_counter): ", len(FL_counter))

fig1, ax1 = plt.subplots()
ax1.plot(BR_counter, BR_y, label='BR')
ax1.set_title('back right encoder analysis')
ax1.set_xlabel('GPIO input reading')
ax1.set_ylabel('encoder state')

fig2, ax2 = plt.subplots()
ax2.plot(FL_counter, FL_y, label='FL')
ax2.set_title('front left encoder analysis')
ax2.set_xlabel('GPIO input reading')
ax2.set_ylabel('encoder state')

#out.release()
#cap.release()

#cv.waitKey(0)
#cv.destoryAllWindows()

plt.show()
gameover()
