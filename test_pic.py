import cv2 as cv

cap = cv.VideoCapture(0)

if not cap.isOpened():
	print("could not open camera")
	exit()

ret, frame = cap.read()

if not ret:
	print("could not capture frame")
	exit()

cv.imshow("captured image", frame)

while True:
	if cv.waitKey(1) & 0xFF == ord('q'):
		break

cap.release()
cv.destroyAllWindows()

cv.imwrite("test_pic.jpg", frame)

