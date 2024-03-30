import RPi.GPIO as gpio
import time
import cv2 as cv

# setup gpio pins and set pin 36 as output 
gpio.setmode(gpio.BOARD)
gpio.setup(36, gpio.OUT)
pwm = gpio.PWM(36, 50)
pwm.start(5) # start PWM frequency to 5% duty cycle

# define video properties
video_file = "dutyCycle.mp4"
min_cycle = 3.5
max_cycle = 7.5

def set_cycle(duty_cycle):
	max_cycle = 9
	if duty_cycle > max_cycle:
		duty_cycle = max_cycle
	pwm.ChangeDutyCycle(duty_cycle)

def write_on_frame(duty_cycle):

	cap = cv.VideoCapture(0)
	if not cap.isOpened():
		print("Error: Could not open camera")
		return

	font = cv.FONT_HERSHEY_SIMPLEX
	location = (15, 25)
	white = (255, 255, 255)
	thickness = 2
	scale = 1

	ret, frame = cap.read()
	frame = cv.flip(frame, 0) # flip across the horizontal axis
	print("duty_cycle to write on frame: ", duty_cycle)
	cv.putText(frame, "Duty: {}%".format(duty_cycle), location, font, scale, white, thickness)
	cv.imwrite("duty_{}.jpg".format(duty_cycle), frame)
	cap.release()

def create_video():

	fps = 1
	fourcc = cv.VideoWriter_fourcc(*'XVID')
	out = cv.VideoWriter('dutyCycle.mp4', fourcc, fps, (640, 480))

	i = 3.5
	j = 7.5

	while i <= 7.5:
		i += 2
#		print("i: ", i)
		frame = cv.imread("duty_{}.jpg".format(i))
		out.write(frame)

	while j >= 3.5:
		j -= 2
#		print("j: ", j)
		frame = cv.imread("duty_{}.jpg".format(j))
		out.write(frame)

def main(duration):

	duty_list = [7.5, 5.5, 3.5, 5.5, 7.5]
	pwm.start(min_cycle)

	for cycle in duty_list:
		print("cycle is: ", cycle)
		set_cycle(cycle)
		write_on_frame(cycle)
		time.sleep(duration)
		print("sleeping...")

	create_video()
	pwm.stop()
	gpio.cleanup()


if __name__ == "__main__":
	# ask user for duration of delay between duty cycles
	duration = input("enter duration in seconds to wait between changing duty cycles: ")
	duration = int(duration)
	time.sleep(duration)
	main(duration)
