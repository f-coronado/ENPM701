import cv2 as cv
import os
import RPi.GPIO as gpio

# setup gpio pins(s)
gpio.setmode(gpio.BOARD)
gpio.setup(36, gpio.OUT)

# initialize pwm signal & move gripper to center position
pwm = gpio.PWM(36, 50)
pwm.start(5.5)
#gpio.output(36, gpio.LOW)

command = 'sudo modprobe bcm2835-v4l2'
os.system(command)

# open video capture
cap = cv.VideoCapture(0)

# define detector
detector = cv.QRCodeDetector()

while True:

	check, img = cap.read()
	data, bbox, _ = detector.detectAndDecode(img)
	
	if(bbox is not None):
		for i in range(len(bbox)):
			cv.line(img, tuple(bbox[i][0]), tuple(bbox[(i+1) % len(bbox)][0]), color = (0, 0, 255), thickness = 4)
#			cv.putText(img, data, (int(bbox[0][0][0]), int(bbox[0][0][1]) - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
	if data:
		print("Data: ", data)
	if data == "HALF":
		pwm.ChangeDutyCycle(5.5)
	if data == "OPEN":
		pwm.ChangeDutyCycle(7.5)
	if data == "CLOSE":
		pwm.ChangeDutyCycle(3.5)

	# show results to the screen
	cv.imshow("QR code detector", img)
	
	# break out of the loop by pressing the q key
	if(cv.waitKey(1) == ord("q")):
		pwm.stop()
		gpio.cleanup()
		break

cap.release()
cv.destroyAllWindows()
