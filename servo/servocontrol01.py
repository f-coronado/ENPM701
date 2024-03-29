import RPi.GPIO as gpio
import time
import cv2 as cv

# setup gpio pins and set pin 36 as output 
gpio.setmode(gpio.BOARD)
gpio.setup(36, gpio.OUT)
pwm = gpio.PWM(36, 50)
pwm.start(5) # start PWM frequency to 5% duty cycle

# initialize camera
cap = cv.VideoCapture(0)
if not cap.isOpened():
	print("couldn't open camera")
	exit()

# define video properties
video_file = "dutyCycle.mp4"
fps = 1
fourcc = cv.VideoWriter_fourcc(*'XVID')
out = cv.VideoWriter('dutyCycle.mp4', fourcc, fps, (int(cap.get(3)), int(cap.get(4))))

min_cycle = 3
max_cycle = 9


def cycle(duration):

	pwm.ChangeDutyCycle(7.5)
	ret, frame = cap.read()
	frame7_5 = cv.putText(frame, "Duty: 7.5%", location, font, scale, white, thickness) 
	time.sleep(duration)

	pwm.ChangeDutyCycle(5.5)
	ret, frame = cap.read()
	frame5_5 = cv.putText(frame, "Duty: 5.5%", location, font, scale, white, thickness) 
	time.sleep(duration)
	
	pwm.ChangeDutyCycle(3.5)
	ret, frame = cap.read()
	frame3_5 = cv.putText(frame, "Duty: 3.5%", location, font, scale, white, thickness) 

def set_cycle(duty_cycle):
	max_cycle = 9
	if duty_cycle > max_cycle:
		duty_cycle = max_cycle
	pwm.ChangeDutyCycle(duty_cycle)

def write_on_frame(duty_cycle):

	font = cv.FONT_HERSHEY_SIMPLEX
	location = (15, 25)
	white = (255, 255, 255)
	thickness = 2
	scale = 1

	ret, frame = cap.read()
	frame = cv.flip(frame, 0) # flip across the horizontal axis

	cv.putText(frame, "Duty: {}%".format(duty_cycle), location, font, scale, white, thickness) 
	cv.imwrite("duty_{}.jpg".format(duty_cycle), frame)
	
#	return frame

def create_video():
	
	for i in range(min_cycle, max_cycle + 1):
		frame = cv.imread("duty_{}.jpg".format(i))
		out.write(frame)
	
#	return out

def main(duration):

	duty_list = [7.5, 5.5, 3.5, 5.5, 7.5]
	pwm.start(min_cycle)

	for cycle in duty_list:
		set_cycle(cycle)
		time.sleep(duration)
		write_on_frame(cycle)
#	for duty_cycle in range(max_cycle - 1, min_cycle - 1, -1):
#		set_cycle(duty_cycle)
#		time.sleep(duration)
#		write_on_frame(duty_cycle)


	create_video()
	pwm.stop()
	gpio.cleanup()
	cap.release()


if __name__ == "__main__":
	# ask user for duration of delay between duty cycles
	duration = input("enter duration: ")
	duration = int(duration)
	main(duration)
